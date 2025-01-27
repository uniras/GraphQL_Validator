import json
from graphql import GraphQLScalarType, build_schema, graphql_sync


class gqlValidator:
    """
    GraphQLのスキーマを使ってJSONデータをバリデーションするクラス
    """
    def __init__(self, schema_definition_source: str, validation_type_name: str, custom_scalar_types: list = None) -> None:
        """
        コンストラクタ
        :param schema_definition_source: バリデーション用のGraphQLスキーマ
        :param validation_type_name: バリデーション対象となる型名
        :param custom_scalar_types: カスタムスカラー型のリスト
        """
        self.gql = schema_definition_source
        self.typename = validation_type_name

        # バリデーション用のクエリを定義したスキーマ
        self.base_input = f"""
            type Query {{
                validate(input: {self.typename}): Boolean
            }}
        """

        # スキーマの構築
        self.schema = build_schema(self.base_input + schema_definition_source)

        # カスタムスカラー型の置き換え
        if custom_scalar_types is not None and isinstance(custom_scalar_types, list) and len(custom_scalar_types) > 0:
            for custom_scalar_type in custom_scalar_types:
                if isinstance(custom_scalar_type, gqlCustomScalarType):
                    # このライブラリのヘルパークラスから継承したカスタムスカラー型の場合は、ヘルパークラス内で生成されているカスタムスカラーを取得
                    scalar_type = custom_scalar_type.scalar
                elif isinstance(custom_scalar_type, GraphQLScalarType):
                    # 既存のGraphQLScalarTypeから定義されたカスタムスカラー型の場合はそのまま使用
                    scalar_type = custom_scalar_type
                else:
                    # 無関係の型の値が指定された場合はエラー
                    raise ValueError("Invalid custom scalar type.")

                # GraphQLスキーマコードで定義したカスタムスカラー型をPythonクラスで定義したカスタムスカラー型に置き換え(このように置き換えないと正しくバリデーションされない)
                self.schema.type_map[scalar_type.name].__dict__.update(scalar_type.__dict__)

    def validate_json(self, input_json_data: str) -> None:
        """
        JSONデータをバリデーションする。成功のときは何もせず、失敗した場合は例外を送出する。
        :param input_json_data: バリデーションするJSONデータ
        """
        data = json.loads(input_json_data)
        self.validate(data)

    def validate(self, validation_data: dict) -> None:
        """
        JSONデータをバリデーションする。成功のときは何もせず、失敗した場合は例外を送出する。
        :param validation_data: バリデーションするdictデータ
        """
        # バリデーション用のGraphQLクエリ
        query = f"""
        query Validate($input: {self.typename}) {{
            validate(input: $input)
        }}
        """

        # データを変数として渡す
        variables = {"input": validation_data}

        # クエリを実行
        result = graphql_sync(self.schema, query, variable_values=variables)

        # エラーチェック
        if result.errors:
            raise ValueError(f"Validation errors: {result.errors}")


class gqlCustomScalarType:
    """
    カスタムスカラー型を定義するためのヘルパークラス
    """
    def __init__(self, name: str, description: str):
        """
        コンストラクタ
        :param name: スカラー型の名前
        :param description: スカラー型の説明
        """
        self.name = name
        self.description = description
        self.scalar = GraphQLScalarType(
            name=name,
            description=description,
            serialize=self.serialize,
            parse_value=self.parse_value,
            parse_literal=self.parse_literal
        )

    def serialize(self, value):
        """
        シリアライズ時の検証
        :param value: 検証する値
        """
        return self.check_value(value)

    def parse_value(self, value):
        """
        パース時の検証
        :param value: 検証する値
        """
        return self.check_value(value)

    def parse_literal(self, node):
        """
        リテラルの検証
        :param node: 検証するノード
        """
        return self.check_value(node.value)

    def check_value(self, value):
        """
        値の検証
        :param value: 検証する値
        """
        return value
