import json
from validator import gqlValidator, gqlCustomScalarType


class TestValueType(gqlCustomScalarType):
    """
    テスト用のカスタムスカラー型
    """
    def __init__(self):
        # スカラ型名と説明の設定
        super().__init__("TestValue", "A number between 0 and 100")

    # バリデーション
    def check_value(self, value) -> int:
        # 型のチェックと変換
        if isinstance(value, int):
            num = value
        else:
            try:
                num = int(value)
            except ValueError:
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
