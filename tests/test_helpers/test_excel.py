"""Tests for ExcelHelper class."""

import os
from pathlib import Path

import openpyxl

from classes.Deck import Deck
from helpers import ExcelHelper


def test_export_to_excel_basic(temp_dir):
    data = [["Alice", 3], ["Bob", 0]]
    headers = ["player", "total"]
    file_path = ExcelHelper.export_to_excel(
        data=data,
        headers=headers,
        file_name="test.xlsx",
        sheet_name="TestSheet",
        output_dir=temp_dir,
    )
    assert file_path.exists()
    assert file_path.name == "test.xlsx"

    wb = openpyxl.load_workbook(file_path)
    assert wb.sheetnames == ["TestSheet"]
    ws = wb.active
    assert [c.value for c in ws[1]] == headers
    assert [c.value for c in ws[2]] == ["Alice", 3]
    assert [c.value for c in ws[3]] == ["Bob", 0]


def test_export_to_excel_dict_rows(temp_dir):
    data = [
        {"card_name": "Swamp", "total": 4},
        {"card_name": "Island", "total": 2},
    ]
    headers = ["card_name", "total"]
    file_path = ExcelHelper.export_to_excel(
        data=data,
        headers=headers,
        file_name="dict_test.xlsx",
        output_dir=temp_dir,
    )
    assert file_path.exists()

    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    assert [c.value for c in ws[1]] == headers
    assert [c.value for c in ws[2]] == ["Swamp", 4]
    assert [c.value for c in ws[3]] == ["Island", 2]


def test_prepare_output_file_creates_dir(temp_dir):
    subdir = temp_dir / "sub" / "nested"
    result = ExcelHelper.prepare_output_file("test.xlsx", output_dir=subdir)
    assert result == subdir
    assert subdir.exists()
    assert subdir.is_dir()


def test_prepare_output_file_removes_existing(temp_dir):
    file_path = temp_dir / "existing.xlsx"
    file_path.write_text("old content")

    result = ExcelHelper.prepare_output_file("existing.xlsx", output_dir=temp_dir)
    assert result == temp_dir
    assert not file_path.exists()  # Should have been removed
