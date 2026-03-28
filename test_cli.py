import typer

app = typer.Typer()


@app.command()
def hello(name: str = typer.Argument(...)):
    typer.echo(f"Hello {name}")


if __name__ == "__main__":
    import sys

    print("argv:", sys.argv)
    app()
