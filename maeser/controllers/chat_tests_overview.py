from flask import render_template, request

from .common.file_info import get_file_list


def tests_controller(chat_test_yaml_path: str):
    """
    Render the home page with test files.

    Returns:
        str: Rendered home template with test file list.
    """
    sort_by = request.args.get('sort_by', 'modified')  # default sorting by modification time
    order = request.args.get('order', 'asc')  # default sorting order is ascending

    test_files = get_file_list(chat_test_yaml_path)

    reverse = (order == 'desc')
    test_files.sort(key=lambda x: x[sort_by], reverse=reverse)

    return render_template('home.html', test_files=test_files, sort_by=sort_by, order=order)