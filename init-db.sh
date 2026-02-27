#!/bin/bash
set -e

export PGPASSWORD="$POSTGRES_PASSWORD"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM pg_database WHERE datname = '$POSTGRES_DB'
        ) THEN
            CREATE DATABASE "$POSTGRES_DB";
        END IF;
    END
    \$\$;
EOSQL
