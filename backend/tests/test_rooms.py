"""
Тесты для всех роутов комнат (Rooms)
Все роуты протестированы с правильной аутентификацией
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from rooms.models import Room, RoomMember, RoomRole


# ============================================
# Тесты создания комнат (POST /rooms/create)
# ============================================

@pytest.mark.asyncio
async def test_create_room_success(client: AsyncClient, test_user: User):
    """Тест успешного создания комнаты"""
    room_data = {
        "name": "Тестовая комната",
        "description": "Описание тестовой комнаты"
    }
    
    response = await client.post("/rooms/create", json=room_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == room_data["name"]
    assert data["description"] == room_data["description"]
    assert data["created_by_id"] == test_user.id
    # Проверяем, что создатель стал владельцем
    assert len(data["members"]) == 1
    assert data["members"][0]["role"] == "owner"


@pytest.mark.asyncio
async def test_create_room_without_description(client: AsyncClient):
    """Тест создания комнаты без описания"""
    room_data = {
        "name": "Комната без описания"
    }
    
    response = await client.post("/rooms/create", json=room_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == room_data["name"]
    assert data["description"] is None


@pytest.mark.asyncio
async def test_create_room_invalid_data(client: AsyncClient):
    """Тест создания комнаты с невалидными данными"""
    room_data = {
        "name": "",  # Пустое название
        "description": "Описание"
    }
    
    response = await client.post("/rooms/create", json=room_data)
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_room_unauthorized(client_unauthorized: AsyncClient):
    """Тест создания комнаты без авторизации"""
    room_data = {
        "name": "Тестовая комната",
        "description": "Описание"
    }
    
    response = await client_unauthorized.post("/rooms/create", json=room_data)
    
    assert response.status_code == 403


# ============================================
# Тесты получения комнат (GET /rooms/get_all)
# ============================================

@pytest.mark.asyncio
async def test_get_all_rooms(client: AsyncClient, test_user: User, test_db: AsyncSession):
    """Тест получения всех комнат пользователя"""
    # Создаем комнаты
    for i in range(3):
        room = Room(
            name=f"Комната {i}",
            description=f"Описание {i}",
            created_by_id=test_user.id
        )
        test_db.add(room)
        await test_db.flush()
        
        # Добавляем пользователя как владельца
        member = RoomMember(
            room_id=room.id,
            user_id=test_user.id,
            role=RoomRole.OWNER
        )
        test_db.add(member)
    
    await test_db.commit()
    
    response = await client.get("/rooms/get_all")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_get_all_rooms_empty(client: AsyncClient):
    """Тест получения комнат когда их нет"""
    response = await client.get("/rooms/get_all")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


# ============================================
# Тесты получения конкретной комнаты (GET /rooms/{room_id})
# ============================================

@pytest.mark.asyncio
async def test_get_room_by_id(client: AsyncClient, test_user: User, test_db: AsyncSession):
    """Тест получения комнаты по ID"""
    room = Room(
        name="Конкретная комната",
        description="Описание",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.get(f"/rooms/{room.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == room.id
    assert data["name"] == room.name


@pytest.mark.asyncio
async def test_get_nonexistent_room(client: AsyncClient):
    """Тест получения несуществующей комнаты"""
    response = await client.get("/rooms/99999")
    
    assert response.status_code == 404


# ============================================
# Тесты обновления комнаты (PUT /rooms/{room_id})
# ============================================

@pytest.mark.asyncio
async def test_update_room_success(client: AsyncClient, test_user: User, test_db: AsyncSession):
    """Тест успешного обновления комнаты владельцем"""
    room = Room(
        name="Старое название",
        description="Старое описание",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    test_db.add(member)
    await test_db.commit()
    await test_db.refresh(room)
    
    update_data = {
        "name": "Новое название",
        "description": "Новое описание"
    }
    
    response = await client.put(f"/rooms/{room.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_update_room_as_admin(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест обновления комнаты админом"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.flush()
    
    # test_user - админ
    member = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.ADMIN
    )
    test_db.add(member)
    await test_db.commit()
    await test_db.refresh(room)
    
    update_data = {"name": "Обновленное название"}
    
    response = await client.put(f"/rooms/{room.id}", json=update_data)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_room_forbidden(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест запрета обновления комнаты обычным участником"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.flush()
    
    # test_user - обычный участник
    member = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.MEMBER
    )
    test_db.add(member)
    await test_db.commit()
    await test_db.refresh(room)
    
    update_data = {"name": "Новое название"}
    
    response = await client.put(f"/rooms/{room.id}", json=update_data)
    
    assert response.status_code == 403


# ============================================
# Тесты удаления комнаты (DELETE /rooms/{room_id})
# ============================================

@pytest.mark.asyncio
async def test_delete_room_success(client: AsyncClient, test_user: User, test_db: AsyncSession):
    """Тест успешного удаления комнаты"""
    room = Room(
        name="Комната для удаления",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.delete(f"/rooms/{room.id}")
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_room_forbidden(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест запрета удаления комнаты не владельцем"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.delete(f"/rooms/{room.id}")
    
    assert response.status_code == 403


# ============================================
# Тесты получения участников (GET /rooms/{room_id}/members)
# ============================================

@pytest.mark.asyncio
async def test_get_room_members(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест получения списка участников комнаты"""
    room = Room(
        name="Комната",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    # Добавляем участников
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.MEMBER
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.get(f"/rooms/{room.id}/members")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_room_members_forbidden(client: AsyncClient, test_user_2: User, test_db: AsyncSession):
    """Тест запрета просмотра участников для не-участника"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.get(f"/rooms/{room.id}/members")
    
    assert response.status_code == 403


# ============================================
# Тесты добавления участников (POST /rooms/{room_id}/members)
# ============================================

@pytest.mark.asyncio
async def test_add_member_success(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест успешного добавления участника владельцем"""
    room = Room(
        name="Комната",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    test_db.add(member)
    await test_db.commit()
    await test_db.refresh(room)
    
    member_data = {
        "user_id": test_user_2.id,
        "role": "member"
    }
    
    response = await client.post(f"/rooms/{room.id}/members", json=member_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_user_2.id
    assert data["role"] == "member"


@pytest.mark.asyncio
async def test_add_member_as_admin(client: AsyncClient, test_user: User, test_user_2: User, test_lead_user: User, test_db: AsyncSession):
    """Тест добавления участника админом"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.flush()
    
    # test_user - админ
    member = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.ADMIN
    )
    test_db.add(member)
    await test_db.commit()
    await test_db.refresh(room)
    
    member_data = {
        "user_id": test_lead_user.id,
        "role": "member"
    }
    
    response = await client.post(f"/rooms/{room.id}/members", json=member_data)
    
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_member_forbidden(client: AsyncClient, test_user: User, test_user_2: User, test_lead_user: User, test_db: AsyncSession):
    """Тест запрета добавления участника обычным участником"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.flush()
    
    # test_user - обычный участник
    member = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.MEMBER
    )
    test_db.add(member)
    await test_db.commit()
    await test_db.refresh(room)
    
    member_data = {
        "user_id": test_lead_user.id,
        "role": "member"
    }
    
    response = await client.post(f"/rooms/{room.id}/members", json=member_data)
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_existing_member(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест попытки добавить уже существующего участника"""
    room = Room(
        name="Комната",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.MEMBER
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    member_data = {
        "user_id": test_user_2.id,
        "role": "member"
    }
    
    response = await client.post(f"/rooms/{room.id}/members", json=member_data)
    
    assert response.status_code == 400


# ============================================
# Тесты удаления участников (DELETE /rooms/{room_id}/members/{user_id})
# ============================================

@pytest.mark.asyncio
async def test_remove_member_by_owner(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест удаления участника владельцем"""
    room = Room(
        name="Комната",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.MEMBER
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.delete(f"/rooms/{room.id}/members/{test_user_2.id}")
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_remove_self_from_room(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест выхода из комнаты (удаление себя)"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.OWNER
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.MEMBER
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.delete(f"/rooms/{room.id}/members/{test_user.id}")
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_remove_owner_forbidden(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест запрета удаления владельца"""
    room = Room(
        name="Комната",
        created_by_id=test_user_2.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.OWNER
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.ADMIN
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    response = await client.delete(f"/rooms/{room.id}/members/{test_user_2.id}")
    
    assert response.status_code == 403


# ============================================
# Тесты изменения роли (PATCH /rooms/{room_id}/members/{user_id}/role)
# ============================================

@pytest.mark.asyncio
async def test_update_member_role_success(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест успешного изменения роли участника"""
    room = Room(
        name="Комната",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.MEMBER
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    role_data = {"role": "admin"}
    
    response = await client.patch(f"/rooms/{room.id}/members/{test_user_2.id}/role", json=role_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_update_role_forbidden_not_owner(client: AsyncClient, test_user: User, test_user_2: User, test_lead_user: User, test_db: AsyncSession):
    """Тест запрета изменения роли не владельцем"""
    room = Room(
        name="Комната",
        created_by_id=test_lead_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    # test_user - админ (не владелец)
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.ADMIN
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.MEMBER
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    role_data = {"role": "admin"}
    
    response = await client.patch(f"/rooms/{room.id}/members/{test_user_2.id}/role", json=role_data)
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_role_to_owner_forbidden(client: AsyncClient, test_user: User, test_user_2: User, test_db: AsyncSession):
    """Тест запрета назначения роли владельца"""
    room = Room(
        name="Комната",
        created_by_id=test_user.id
    )
    test_db.add(room)
    await test_db.flush()
    
    member1 = RoomMember(
        room_id=room.id,
        user_id=test_user.id,
        role=RoomRole.OWNER
    )
    member2 = RoomMember(
        room_id=room.id,
        user_id=test_user_2.id,
        role=RoomRole.MEMBER
    )
    test_db.add_all([member1, member2])
    await test_db.commit()
    await test_db.refresh(room)
    
    role_data = {"role": "owner"}
    
    response = await client.patch(f"/rooms/{room.id}/members/{test_user_2.id}/role", json=role_data)
    
    assert response.status_code == 403
