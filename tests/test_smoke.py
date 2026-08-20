def test_saturn_package_importable():
    import saturn

    assert saturn.__version__ == "0.1.0"
