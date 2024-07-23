import json


def generate_notebook(cells):
    new_cells = [
        generate_notebook_one_cell(
            cell["role"],
            text=cell.get("text", None),
            code=cell.get("code", None),
            result=cell.get("result", None),
        )
        for cell in cells
    ]
    return new_cells


def generate_notebook_one_cell(role, text=None, code=None, result=None):
    if text is not None and code is None and result is None:
        # 仅传入文本内容，生成Markdown单元格
        cell = {"cell_type": "markdown", "metadata": {}, "source": f"<|{role}|>\n\n{text}"}
    elif code is not None and result is not None:
        # 传入文本、代码和执行结果，生成Code单元格
        cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [{"name": "stdout", "text": [result], "output_type": "stream"}],
            "source": [code],
        }
    else:
        raise ValueError("Invalid combination of parameters.")

    return cell


def save_as_ipynb(cells, filename):
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.7.11",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    with open(filename, "w") as file:
        json.dump(notebook, file, indent=2)

    print(f"Notebook saved as {filename}")


if __name__ == "__main__":
    messasges = [
        {
            "role": "system",
            "content": "You are a proficient Data Scientist who good at data analysis.",
        },
        {"role": "user", "content": "What is the result of 2^1000"},
        {"role": "assistant", "content": "The result is:"},
    ]
