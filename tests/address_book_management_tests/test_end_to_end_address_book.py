from bll.services.record_service.record_service import RecordService
from dal.entities.record import Record
from dal.storages.address_book_storage import AddressBookStorage


def test_end_to_end_scenario():
    book = AddressBookStorage()
    service = RecordService(book)

    john = Record("John", "+380123456789")
    jane = Record("Jane", "+380987654321")

    service.save(john)
    service.save(jane)

    assert service.has("John")
    assert service.has("Jane")

    # ТВОЯ НОВА ЛОГІКА → update_phone НЕ ІСНУЄ
    john_builder = john.update()
    john_builder.remove_phone("+380123456789")
    john_builder.add_phone("+380111222333")
    updated_john = john_builder.build()

    service.update("John", updated_john)

    updated = service.get_by_name("John")
    assert updated.phones[0].value == "+380111222333"

    renamed = service.rename("John", "Johnny")
    assert renamed.name.value == "Johnny"
    assert not service.has("John")
    assert service.has("Johnny")

    service.delete("Jane")
    assert not service.has("Jane")

    all_records = service.get_all()
    assert len(all_records) == 1
    assert all_records[0].name.value == "Johnny"
