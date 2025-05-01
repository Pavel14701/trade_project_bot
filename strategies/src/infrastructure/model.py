from sqlalchemy import text
from sqlalchemy.sql import quoted_name

from strategies.src.application.interfaces import IDataQueryBuilder
from strategies.src.domain.entities import (
    CreateTableDM,
    GetLastRecordsDM,
    GetRangeRecordsDM,
    InsertManyRecordsDM,
    InsertRecordDM,
)


class DataQueryBuilder(IDataQueryBuilder):
    def create_datatable(self, params: CreateTableDM) -> str:
        table_name = quoted_name(
            f"{params.instId}_{params.bar}_data",
            quote=True
        )
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
            ) TIMESTAMP(date) PARTITION BY :partition_type;
        """).bindparams(
            table_name=table_name, 
            partition_type=partition_type
        )
        return str(query)

    def get_last_records(self, params: GetLastRecordsDM) -> str:
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
        return str(query)

    def get_records_by_date_range(self, params: GetRangeRecordsDM) -> str:
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
        return str(query)

    def insert_record(self, params: InsertRecordDM) -> str:
        table_name = quoted_name(
            f"{params.instId}_{params.bar}_data",
            quote=True
        )
        query = text("""
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
                )
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
        return str(query)

    def generate_insert_query(self, params: InsertManyRecordsDM) -> str:
        """Генерирует SQL-запрос с SQLAlchemy для вставки batch данных."""
        table_name = quoted_name(
            f"{params.instId}_{params.bar}_data", 
            quote=True
        )
        values_sql = ", ".join(
            f"(:date{i}, :open_price{i}, \
                :close_price{i}, :high_price{i}, \
                :low_price{i}, :volume{i}, \
                :turnover{i})"
            for i in range(len(params.data))
        )
        query = text(f"""
            INSERT INTO :table_name 
                (
                    date, open_price, close_price, 
                    high_price, low_price, volume, 
                    turnover
                )
            VALUES {values_sql}
        """)
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
        query.bindparams(
            **bind_params,
            table_name=table_name
        )
        return str(query)