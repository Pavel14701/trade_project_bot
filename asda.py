from datasets.database import DataAllDatasets, classes_dict, Session

db = DataAllDatasets('BTC-USDT-SWAP', '4H', Session, classes_dict)
db.