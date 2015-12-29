# -*- coding: utf-8 -*-
from numbers import Number
try:
    import xlsxwriter
    import xlrd
except ImportError:
    xlsxwriter = None
    xlrd = None

try:
    basestring
except NameError:
    basestring = str


def get_sheet_from_file(directory, sheet_idx=None, sheet_name=None):
    """both idx and name could be a list, then a list of sheets will be returned."""
    if sheet_idx is not None:
        if isinstance(sheet_idx, int):
            return xlrd.open_workbook(directory).sheet_by_index(sheet_idx)
        elif isinstance(sheet_idx, list):
            return [xlrd.open_workbook(directory).sheet_by_index(idx) for idx in sheet_idx]
        else:
            raise TypeError('invalid sheet_idx: %s' % sheet_idx)
    elif sheet_name is not None:
        if isinstance(sheet_idx, basestring):
            return xlrd.open_workbook(directory).sheet_by_name(sheet_name)
        elif isinstance(sheet_idx, list):
            return [xlrd.open_workbook(directory).sheet_by_name(name) for name in sheet_name]
        else:
            raise TypeError('invalid sheet_name: %s' % sheet_name)
    else:
        raise ValueError('both sheet_idx & sheet_name is None, what do you want?')


def get_subframe(sheet, col_idxs, row_offset, row_limit=None):
    """get sub dataframe from sheet
    return value is like:
    [[1, 2, 3],
     [8, 9, 0]]
    """
    df = []
    row_range = row_offset + row_limit if row_limit else sheet.nrows
    for i in range(row_offset, row_range):
        df.append([sheet.cell(i, j).value for j in col_idxs])
    return df


def write_excel(file_name, sheets=[]):
    """sheet is like:
    {
        'name': 'sheet1',
        'data': [[1, 2, 3],
                 [8, 9, 0]]
    }
    """
    workbook = xlsxwriter.Workbook('%s.xlsx' % file_name)
    for sheet in sheets:
        worksheet = workbook.add_worksheet(name=sheet['name'])
        for i in range(len(sheet['data'])):
            for j in range(len(sheet['data'][i])):
                if isinstance(sheet['data'][i][j], Number):
                    worksheet.write_number(i, j, int(sheet['data'][i][j]))
                elif isinstance(sheet['data'][i][j], basestring):
                    worksheet.write_string(i, j, sheet['data'][i][j])
                else:
                    worksheet.write_blank(i, j, sheet['data'][i][j])
    workbook.close()
