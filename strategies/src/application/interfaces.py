from typing import Protocol

from strategies.src.domain.entities import (
    CreateTableDM,
    GetLastRecordsDM,
    GetRangeRecordsDM,
    InsertManyRecordsDM,
    InsertRecordDM,
)


class IDataQueryBuilder(Protocol):
    def create_datatable(self, params: CreateTableDM) -> str:
        ...

    def get_last_records(self, params: GetLastRecordsDM) -> str:
        ...

    def get_records_by_date_range(self, params: GetRangeRecordsDM) -> str:
        ...

    def insert_record(self, params: InsertRecordDM) -> str:
        ...

    def generate_insert_query(self, params: InsertManyRecordsDM) -> str:
        ...