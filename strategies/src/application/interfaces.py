from typing import Protocol

from strategies.src.domain.entities import (
    CreateTableDM,
    GetLastRecordsDM,
    GetRangeRecordsDM,
    InsertManyRecordsDM,
    InsertRecordDM,
)
from strategies.src.infrastructure._types import PriceDataFrame


class IDataQuery(Protocol):
    async def create_datatable(self, params: CreateTableDM) -> bool:
        ...

    async def get_last_records(
        self, 
        params: GetLastRecordsDM
    ) -> PriceDataFrame:
        ...

    async def get_records_by_date_range(
        self, 
        params: GetRangeRecordsDM
    ) -> PriceDataFrame:
        ...

    async def insert_record(self, params: InsertRecordDM) -> bool:
        ...

    async def insert_many_data(self, params: InsertManyRecordsDM) -> bool:
        ...