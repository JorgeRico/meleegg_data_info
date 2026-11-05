from pathlib import Path

from openpyxl import Workbook


class ExcelHelper:
    OUTPUT_FILES_DIR = Path(__file__).resolve().parent.parent / "output_files"

    @classmethod
    def prepare_output_file(cls, file_name: str, output_dir: Path | None = None) -> Path:
        """Ensure the output directory exists and remove any existing file.

        Args:
            file_name: Name of the file to prepare.
            output_dir: Target directory (defaults to output_files/).

        Returns:
            Path to the output directory.
        """
        target_dir = output_dir or cls.OUTPUT_FILES_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        existing_file = target_dir / file_name
        if existing_file.exists():
            existing_file.unlink()
        return target_dir

    @classmethod
    def export_to_excel(
        cls,
        data,
        headers,
        file_name: str,
        sheet_name: str = "Sheet1",
        output_dir: Path | None = None,
    ) -> Path:
        """Export a list of rows to an Excel file.

        Args:
            data: Iterable of rows (dict or list/tuple).
            headers: List of column names.
            file_name: Output file name.
            sheet_name: Worksheet name.
            output_dir: Directory to save the file (defaults to output_files/).

        Returns:
            Path to the saved Excel file.
        """
        target_dir = output_dir or cls.OUTPUT_FILES_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = sheet_name
        sheet.append(headers)

        for row in data:
            if isinstance(row, dict):
                sheet.append([row.get(h, "") for h in headers])
            else:
                sheet.append(list(row))

        file_path = target_dir / file_name
        workbook.save(file_path)
        return file_path
