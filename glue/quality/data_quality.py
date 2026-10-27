
from pyspark.sql.functions import col


class DataQuality:

    def __init__(self):
        self.results = []

    def _record_result(self, check_name, status, details):
        self.results.append({
            "check": check_name,
            "status": status,
            "details": details
        })

    def check_nulls(self, df, columns):

        for column in columns:

            count = df.filter(col(column).isNull()).count()

            if count == 0:
                self._record_result(
                    f"Null Check ({column})",
                    "PASS",
                    "No null values"
                )
            else:
                self._record_result(
                    f"Null Check ({column})",
                    "FAIL",
                    f"{count} null values"
                )

    def check_duplicates(self, df, column):

        duplicate_count = (
            df.groupBy(column)
              .count()
              .filter(col("count") > 1)
              .count()
        )

        if duplicate_count == 0:
            self._record_result(
                f"Duplicate Check ({column})",
                "PASS",
                "No duplicate values"
            )
        else:
            self._record_result(
                f"Duplicate Check ({column})",
                "FAIL",
                f"{duplicate_count} duplicate keys"
            )

    def check_positive_values(self, df, column):

        invalid = df.filter(col(column) <= 0).count()

        if invalid == 0:
            self._record_result(
                f"Positive Value Check ({column})",
                "PASS",
                "All values positive"
            )
        else:
            self._record_result(
                f"Positive Value Check ({column})",
                "FAIL",
                f"{invalid} invalid values"
            )

    def check_referential_integrity(
        self,
        child_df,
        parent_df,
        child_column,
        parent_column
    ):

        missing = (
            child_df.alias("child")
            .join(
                parent_df.alias("parent"),
                col(f"child.{child_column}")
                == col(f"parent.{parent_column}"),
                "left_anti"
            )
            .count()
        )

        if missing == 0:
            self._record_result(
                f"Referential Integrity ({child_column})",
                "PASS",
                "All foreign keys valid"
            )
        else:
            self._record_result(
                f"Referential Integrity ({child_column})",
                "FAIL",
                f"{missing} orphan records"
            )

    def get_results(self):
        return self.results