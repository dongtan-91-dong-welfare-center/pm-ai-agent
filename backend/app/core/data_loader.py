import os
import pandas as pd
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


class DataLoader:
    """Singleton that loads all CSV files from the data directory into pandas DataFrames."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return
        base = os.path.abspath(DATA_DIR)
        self.product = pd.read_csv(os.path.join(base, "product.csv"), dtype=str)
        self.warehouse_stock = pd.read_csv(os.path.join(base, "warehouse_stock.csv"))
        self.batch_stock = pd.read_csv(os.path.join(base, "batch_stock.csv"), parse_dates=["manufacture_date", "expiration_date", "receipt_date"])
        self.bom = pd.read_csv(os.path.join(base, "bom.csv"))
        self.production_plan = pd.read_csv(os.path.join(base, "production_plan.csv"), parse_dates=["start_date", "end_date"])
        self.purchase_order = pd.read_csv(os.path.join(base, "purchase_order.csv"), parse_dates=["po_date", "delivery_date"])
        self.purchase_transaction_history = pd.read_csv(os.path.join(base, "purchase_transaction_history.csv"), parse_dates=["receipt_date"])
        self.good_receipt = pd.read_csv(os.path.join(base, "good_receipt.csv"), parse_dates=["work_datetime", "manufacturing_date", "expiration_date"])
        self.vendor = pd.read_csv(os.path.join(base, "vendor.csv"), dtype=str)
        self.vendor_into_record = pd.read_csv(os.path.join(base, "vendor_into_record.csv"), parse_dates=["valid_from"])
        self.material_ledger = pd.read_csv(os.path.join(base, "material_ledger.csv"))
        self.non_conformance = pd.read_csv(os.path.join(base, "non_conformance.csv"), parse_dates=["posting_date", "document_date"])
        self.overage_rules = pd.read_csv(os.path.join(base, "overage_rules.csv"), dtype=str)
        self.prod_plan_code_map = pd.read_csv(os.path.join(base, "prod_plan_code_map.csv"), dtype=str)
        self._loaded = True


@lru_cache(maxsize=1)
def get_data_loader() -> DataLoader:
    loader = DataLoader()
    loader.load()
    return loader
