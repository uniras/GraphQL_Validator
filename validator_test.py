import json
from validator import gqlValidator, gqlCustomScalarType


class TestValueType(gqlCustomScalarType):
    """
    テスト用のカスタムスカラー型

    ・0から100までの整数を受け付け、それ以外の値や整数以外は基本的にエラーとする。
    ・ただし浮動小数点値の場合は小数点を切り捨て整数に変換した上で範囲チェックを行う。
    """
    def __init__(self):
        """
        スカラ型名と説明の設定
        """
        super().__init__("TestValue", "A number between 0 and 100")

    def check_value(self, value) -> int:
        """
        値の型変換と範囲のチェック
        """
        # 型の確認および変換
        if isinstance(value, int):
            num = value
        else:
            try:
                # 整数値に変換できる場合はそのまま変換
                num = int(value)
            except ValueError:
                # 整数値に変換できない場合は一度浮動小数点値として変換した上で整数に変換
                # ここで変換に失敗した場合は例外が送出される
                num = int(float(value))

        # 範囲のチェック
        if num < 0 or num > 100:
            # 範囲外でエラーとする場合は例外を送出
            raise ValueError(f"Value must be between 0 and 100. Got {value}.")

        # 範囲内で正常な場合は値をそのまま返す
        return num


# スキーマの定義
gql = """
scalar TestValue

input TestType {
    japanese: TestValue!
    math: TestValue!
    science: TestValue!
    english: TestValue!
    history: TestValue!
}
"""

# データの定義
jsondata = """
{
    "japanese": 100,
    "math": 90,
    "science": 80,
    "english": 70,
    "history": 60
}
"""

data = json.loads(jsondata)

# バリデータの作成
validator = gqlValidator(gql, "TestType!", [TestValueType()])

# データのバリデーション(正常)
try:
    validator.validate_json(jsondata)
    print("Validation successful")
except ValueError as e:
    print(f"Validation failed: {e}")


# データの変更
data["math"] = 800

# データのバリデーション(異常1)
try:
    validator.validate(data)
    print("Validation successful")
except ValueError as e:
    print(f"Validation failed: {e}")

# データの変更
data["math"] = "invalid"

# データのバリデーション(異常2)
try:
    validator.validate(data)
except ValueError as e:
    print(f"Validation failed: {e}")
