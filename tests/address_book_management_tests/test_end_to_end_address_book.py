from bll.services.record_service.record_service import RecordService
from dal.entities.record import Record
from dal.storages.address_book_storage import AddressBookStorage


def test_end_to_end_scenario():
    # --- core init ---
    book = AddressBookStorage()
    service = RecordService(book)

    # --- data init ---
    john = Record("John", "+380123456789")
    jane = Record("Jane", "+380987654321")

    service.save(john)
    service.save(jane)

    # --- existence checks ---
    assert service.has("John")
    assert service.has("Jane")

    # --- update John's phone ---
    john_builder = john.update()
    john_builder.update_phone("+380123456789", "+380111222333")
    updated_john = john_builder.build()
    service.update("John", updated_john)

    # --- verify phone update ---
    updated = service.get_by_name("John")
    assert updated.phones[0].value == "+380111222333"

    # --- rename John to Johnny ---
    renamed = service.rename("John", "Johnny")

    assert renamed.name.value == "Johnny"
    assert not service.has("John")
    assert service.has("Johnny")

    # --- delete Jane ---
    service.delete("Jane")

    assert not service.has("Jane")

    # --- final state check ---
    all_records = service.get_all()
    assert len(all_records) == 1
    assert all_records[0].name.value == "Johnny"









