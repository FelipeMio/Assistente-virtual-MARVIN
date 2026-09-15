from marvin.notifications import NotificationManager


def test_notification_lifecycle(tmp_path):
    storage = (
        tmp_path
        / "notifications.json"
    )

    manager = NotificationManager(
        storage_file=storage,
    )

    first = manager.adicionar(
        origem="Teste",
        titulo="Primeira",
        mensagem="Mensagem 1",
    )

    second = manager.adicionar(
        origem="Teste",
        titulo="Segunda",
        mensagem="Mensagem 2",
    )

    assert (
        manager.quantidade_nao_lidas()
        == 2
    )

    items = manager.listar()

    assert [
        item["id"]
        for item in items
    ] == [
        second,
        first,
    ]

    assert (
        manager.marcar_como_lida(
            second
        )
        is True
    )

    assert (
        manager.marcar_como_lida(
            second
        )
        is False
    )

    assert (
        manager.quantidade_nao_lidas()
        == 1
    )

    # Confirma persistencia em disco.
    reloaded = NotificationManager(
        storage_file=storage,
    )

    assert (
        reloaded.quantidade_nao_lidas()
        == 1
    )

    loaded = reloaded.listar()

    assert loaded[0]["id"] == second
    assert loaded[0]["lida"] is True

    assert (
        reloaded.marcar_todas_como_lidas()
        is True
    )

    assert (
        reloaded.quantidade_nao_lidas()
        == 0
    )

    reloaded.limpar()

    assert reloaded.listar() == []


def test_notification_history_limit(
    tmp_path
):
    manager = NotificationManager(
        storage_file=(
            tmp_path
            / "notifications.json"
        ),
        history_limit=2,
    )

    first = manager.adicionar(
        "Teste",
        "1",
        "Primeira",
    )

    second = manager.adicionar(
        "Teste",
        "2",
        "Segunda",
    )

    third = manager.adicionar(
        "Teste",
        "3",
        "Terceira",
    )

    ids = [
        item["id"]
        for item in manager.listar()
    ]

    assert ids == [
        third,
        second,
    ]

    assert first not in ids
