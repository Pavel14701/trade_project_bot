from sqlalchemy import event, inspect
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.properties import ColumnProperty
# Для отслеживания изменений после флаш (использовалась для тестов)


def get_old_value(attribute_state):
    history = attribute_state.history
    return history.deleted[0] if history.deleted else None


def trigger_attribute_change_events(object_):
    for mapper_property in object_mapper(object_).iterate_properties:
        if isinstance(mapper_property, ColumnProperty):
            key = mapper_property.key
            attribute_state = inspect(object_).attrs.get(key)
            history = attribute_state.history
            if history.has_changes():
                value = attribute_state.value
                old_value = get_old_value(attribute_state)
                # Обработка изменения атрибута
                # Например, можно вызвать метод обновления здесь


def on_after_flush(session, flush_context):
        changed_objects = session.new.union(session.dirty)
        for o in changed_objects:
            trigger_attribute_change_events(o)


# event.listen(session, "after_flush", on_after_flush)