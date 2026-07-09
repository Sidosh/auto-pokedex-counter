def test_set_sprites_per_row_window_fits_the_last_column(main_window, qtbot):
    """Regression test: the fixed window width must include the outer
    QVBoxLayout's own margins (main_window.py's _build_ui), not just
    SpriteStrip's natural_width() - otherwise the last column gets clipped."""
    main_window.set_sprites_per_row(5)
    main_window.show()
    qtbot.waitExposed(main_window)

    layout = main_window.sprite_strip._layout
    last_item = layout.itemAt(4).geometry()

    assert last_item.x() + last_item.width() <= main_window.sprite_strip.width()
