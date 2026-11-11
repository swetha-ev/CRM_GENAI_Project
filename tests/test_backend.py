import unittest

import pandas as pd

import backend
import visualization


class SQLValidationTests(unittest.TestCase):
    def test_select_is_allowed(self) -> None:
        self.assertTrue(backend.validate_sql("SELECT customer_id FROM customers"))

    def test_cte_select_is_allowed(self) -> None:
        self.assertTrue(
            backend.validate_sql(
                "WITH totals AS (SELECT customer_id FROM orders) "
                "SELECT customer_id FROM totals"
            )
        )

    def test_data_changing_statement_is_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("DELETE FROM customers")

    def test_select_without_crm_source_is_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("SELECT 1")

    def test_external_database_is_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("SELECT user FROM mysql.user")

    def test_multiple_statements_are_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("SELECT 1; DROP TABLE customers")

    def test_select_into_is_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("SELECT customer_id INTO OUTFILE 'customers.csv' FROM customers")

    def test_locked_select_is_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("SELECT customer_id FROM customers FOR UPDATE")

    def test_restricted_function_is_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("SELECT SLEEP(5)")

    def test_malformed_sql_is_rejected(self) -> None:
        with self.assertRaises(backend.SQLValidationError):
            backend.validate_sql("SELECT FROM")


class VisualizationTests(unittest.TestCase):
    def test_single_value_has_no_chart(self) -> None:
        dataframe = pd.DataFrame({"total_sales": [100]})
        self.assertIsNone(visualization.auto_visualize(dataframe, "What are total sales?"))

    def test_categorical_values_produce_bar_chart(self) -> None:
        dataframe = pd.DataFrame({"status": ["Won", "Lost"], "lead_count": [4, 2]})
        figure = visualization.auto_visualize(dataframe, "Show leads by status")
        self.assertIsNotNone(figure)
        self.assertEqual(figure.layout.xaxis.title.text, "Status")


if __name__ == "__main__":
    unittest.main()
