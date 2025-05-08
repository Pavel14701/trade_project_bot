from httpx import AsyncClient, Response
from sqlalchemy import text
from sqlalchemy.sql import quoted_name

from strategies.src.application.interfaces import IDataQuery
from strategies.src.config import QuestConfig
from strategies.src.domain.entities import (
    CreateTableDM,
    GetLastRecordsDM,
    GetRangeRecordsDM,
    InsertManyRecordsDM,
    InsertRecordDM,
)
from strategies.src.infrastructure._types import PriceDataFrame


class DataQueryRepo(IDataQuery):
    def __init__(
        self,
        httpx_client: AsyncClient,
        config: QuestConfig
    ) -> None:
        self._client = httpx_client
        self._config = config

    async def create_datatable(self, params: CreateTableDM) -> bool:
        table_name = quoted_name(f"{params.instId}_{params.bar}_data", quote=True)
        partition_type = params.partition.upper() if params.partition else "NONE"
        query = text("""
            CREATE TABLE :table_name (
                date TIMESTAMP,
                open_price DOUBLE,
                close_price DOUBLE, 
                high_price DOUBLE,
                low_price DOUBLE,
                volume LONG,
                turnover DOUBLE 
            ) TIMESTAMP(date) PARTITION BY :partition_type WAL;
        """).bindparams(
            table_name=table_name, 
            partition_type=partition_type
        )
        response = await self._client.post(self._config.url, params=str(query))
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return True

    async def get_last_records(
        self, 
        params: GetLastRecordsDM
    ) -> PriceDataFrame:
        table_name = quoted_name(
            f"{params.instId}_{params.bar}_data",
            quote=True
        )
        query = text("""
            SELECT * FROM :table_name
            ORDER BY date DESC
            LIMIT :n
        """).bindparams(
            table_name=table_name, 
            n=params.n
        )
        response = await self._client.post(self._config.url, params=str(query))
        return self._response_mapper(response)

    async def get_records_by_date_range(
        self, 
        params: GetRangeRecordsDM
    ) -> PriceDataFrame:
        table_name = quoted_name(
            f"{params.instId}_{params.bar}_data", quote=True
        )
        query = text("""
            SELECT * FROM :table_name
            WHERE date BETWEEN :start_date AND :end_date
            ORDER BY date ASC
        """).bindparams(
            table_name=table_name, 
            start_date=params.start_date,
            end_date=params.end_date,
        )
        response = await self._client.post(
            self._config.url, 
            params=str(query)
        )
        return self._response_mapper(response)

    async def insert_record(self, params: InsertRecordDM) -> bool:
        table_name = quoted_name(
            f"{params.instId}_{params.bar}_data",
            quote=True
        )
        query = text("""
            BEGIN;
            INSERT INTO :table_name 
                (
                    date, open_price, close_price, 
                    high_price, low_price, volume, 
                    turnover
                )
            VALUES 
                (
                    :date, :open_price, :close_price, 
                    :high_price, :low_price, :volume,
                    :turnover
                );
            COMMIT;
        """).bindparams(
            table_name=table_name, 
            date=params.date,
            open_price=params.open_price, 
            close_price=params.close_price,
            high_price=params.high_price, 
            low_price=params.low_price, 
            volume=params.volume, 
            turnover=params.turnover
        ) 
        response = await self._client.post(
            self._config.url, 
            params={"query": str(query)}
        )
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return True

    async def insert_many_data(self, params: InsertManyRecordsDM) -> bool:
        table_name = quoted_name(f"{params.instId}_{params.bar}_data", quote=True)
        values_sql = ", ".join(
            f"""(
                :date{i}, :open_price{i}, :close_price{i},
                :high_price{i}, :low_price{i}, :volume{i},
                :turnover{i}
            )"""
            for i in range(len(params.data))
        )
        query = text("""
            BEGIN;
            INSERT INTO :table_name 
                (
                    date, open_price, close_price, 
                    high_price, low_price, volume, 
                    turnover
                )
            VALUES """ + values_sql + "; COMMIT;"
        ).bindparams(table_name=table_name)
        bind_params: dict[str, float | int | str] = {}
        for i, record in enumerate(params.data):
            bind_params |= {
                f"date{i}": record.date,
                f"open_price{i}": record.open_price,
                f"close_price{i}": record.close_price,
                f"high_price{i}": record.high_price,
                f"low_price{i}": record.low_price,
                f"volume{i}": record.volume,
                f"turnover{i}": record.turnover,
            }
        query = query.bindparams(**bind_params)
        response = await self._client.post(
            self._config.url, 
            params={"query": str(query)}
        )
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return True

    def _response_mapper(self, response: Response) -> PriceDataFrame:
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        data = response.json()["dataset"]
        columns = response.json()["columns"]
        return PriceDataFrame(data, columns=columns)