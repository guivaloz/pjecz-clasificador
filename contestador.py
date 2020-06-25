import click
import sys
from datetime import datetime
from comunes.config import pass_config
from clientes.clientes import Clientes
from depositos.deposito import Deposito


@click.group()
@click.option('--fecha', default='', type=str, help='Fecha AAAA-MM-DD')
@click.option('--rama', default='', type=str, help='Acuerdos, Edictos, EdictosJuzgados o Sentencias')
@pass_config
def cli(config, fecha, rama):
    click.echo('Hola, ¡soy Clasificador!')
    # Fecha
    if fecha != '':
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
            config.fecha = fecha
        except ValueError:
            click.echo('ERROR: Fecha incorrecta.')
            sys.exit(1)
    # Rama
    config.rama = rama.title()
    if config.rama not in ('Acuerdos', 'Edictos', 'Edictosjuzgados', 'Sentencias'):
        click.echo('ERROR: Rama no programada.')
        sys.exit(1)
    # Configuración
    try:
        config.cargar_configuraciones()
    except Exception:
        click.echo('ERROR: Falta configuración en settings.ini')
        sys.exit(1)


@cli.command()
@pass_config
def informar(config):
    """ Informar con una línea breve en pantalla """
    click.echo('Voy a informar...')
    click.echo(f'Rama:     {config.rama}')
    click.echo(f'Fecha:    {config.fecha}')
    click.echo(f'e-mail:   {config.email_direccion}')
    click.echo(f'Depósito: {config.deposito_ruta}')
    clientes = Clientes(config)
    clientes.alimentar()
    click.echo(repr(clientes))
    click.echo(clientes.crear_tabla())
    sys.exit(0)


@cli.command()
@pass_config
def rastrear(config):
    """ Rastrear documentos en la rama y fecha dada """
    click.echo('Voy a rastrear...')
    deposito = Deposito(config)
    deposito.rastrear()
    if deposito.cantidad == 0:
        click.echo(f'AVISO: No se encontraron documentos con fecha {config.fecha}')
    else:
        for documento in deposito.documentos:
            click.echo(documento.ruta)
    sys.exit(0)


@cli.command()
@click.option('--enviar', is_flag=True, help='Enviar mensajes')
@pass_config
def responder(config, enviar):
    """ Responder con un mensaje vía correo electrónico """
    click.echo('Voy a rastrear y responder...')
    clientes = Clientes(config)
    clientes.alimentar()
    deposito = Deposito(config)
    deposito.rastrear()
    if deposito.cantidad == 0:
        click.echo(f'AVISO: No se encontraron documentos con fecha {config.fecha}')
        sys.exit(0)
    for documento in deposito.documentos:
        destinatarios = clientes.filtrar_con_archivo_ruta(documento.ruta)
        if len(destinatarios) == 0:
            click.echo(f'AVISO: No hay destinatarios para {documento.ruta}')
        else:
            for email, informacion in destinatarios.items():
                documento.definir_acuse()
                if enviar:
                    documento.enviar_acuse(email)
                else:
                    click.echo(f"- SIMULO envar mensaje a {email} sobre {documento.archivo}")
                    click.echo(documento.acuse.asunto)
                    click.echo(documento.acuse.contenido)
                    click.echo()
    sys.exit(0)


cli.add_command(informar)
cli.add_command(rastrear)
cli.add_command(responder)
