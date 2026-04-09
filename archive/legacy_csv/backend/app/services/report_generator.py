import pandas as pd
import io
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def generate_excel_report(data: pd.DataFrame, title: str = "MatAgent Report") -> bytes:
    """
    Pandas DataFrame을 스타일이 적용된 엑셀 바이너리로 변환합니다.
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="Report")
        workbook = writer.book
        worksheet = writer.sheets["Report"]
        
        # Style Header
        header_fill = PatternFill(start_color="30D796", end_color="30D796", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border
            
        # Auto-adjust column width
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column].width = adjusted_width

    return output.getvalue()
