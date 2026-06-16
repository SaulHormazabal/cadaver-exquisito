from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from corpse.models import Fragment, Story

User = get_user_model()

USUARIOS = [
    {
        "email": "valentina@example.com",
        "display_name": "Valentina Rojas",
        "bio": "Escritora de cuentos breves y amante del surrealismo latinoamericano.",
    },
    {
        "email": "mateo@example.com",
        "display_name": "Mateo Cifuentes",
        "bio": "Poeta visual. Mezcla palabras e imágenes para crear mundos imposibles.",
    },
    {
        "email": "isadora@example.com",
        "display_name": "Isadora Pinto",
        "bio": "Narradora oral. Le gustan las historias que no tienen final claro.",
    },
    {
        "email": "felix@example.com",
        "display_name": "Félix Andrade",
        "bio": "Lector compulsivo de ciencia ficción y cronista de lo cotidiano.",
    },
    {
        "email": "camila@example.com",
        "display_name": "Camila Soto",
        "bio": "Escribe en cafeterías ruidosas. Sus personajes siempre tienen hambre.",
    },
    {
        "email": "rodrigo@example.com",
        "display_name": "Rodrigo Vega",
        "bio": "Aficionado al teatro y a las oraciones larguísimas sin puntos.",
    },
]

HISTORIAS = [
    {
        "title": "El viaje del cartero perdido",
        "prompt": "Un cartero que lleva años entregando cartas que nunca llegan.",
        "visibility": Story.Visibility.TAIL,
        "tail_words": 5,
        "max_fragments": 4,
        "fragmentos": [
            {
                "author_index": 0,
                "text": (
                    "El cartero Aurelio llevaba diecisiete años caminando por calles que no "
                    "aparecían en ningún mapa. Sus botas habían tocado adoquines de ciudades "
                    "que quizás nunca existieron, y sin embargo el maletín seguía pesando lo mismo: "
                    "ciento cuarenta y dos cartas sin destinatario conocido."
                ),
            },
            {
                "author_index": 1,
                "text": (
                    "En el cruce de la calle Transparente con el callejón del Olvido, una mujer "
                    "vestida de lluvia le preguntó si traía algo para ella. Aurelio revisó el maletín "
                    "y encontró un sobre con su propio nombre escrito con letra que no reconoció, "
                    "aunque era idéntica a la suya de los veinte años."
                ),
            },
            {
                "author_index": 2,
                "text": (
                    "Dentro del sobre había una fotografía de un jardín en invierno y una nota que "
                    "decía: «Llegas tarde, pero llegas». Aurelio no supo si aquello era una bienvenida "
                    "o una despedida, de modo que dobló el papel con cuidado, lo guardó en el bolsillo "
                    "izquierdo, y siguió caminando hacia el norte, que para él siempre había sido el sur."
                ),
            },
            {
                "author_index": 3,
                "text": (
                    "Al llegar a la orilla de un río que olía a tinta, Aurelio abrió el maletín por "
                    "última vez. Las ciento cuarenta y dos cartas se habían convertido en pájaros de papel "
                    "que volaron hacia un cielo color naranja. El maletín quedó vacío, liviano, "
                    "casi feliz. Por primera vez en diecisiete años, el cartero supo que había llegado."
                ),
            },
        ],
    },
    {
        "title": "La ciudad que nunca durmió",
        "prompt": "Una metrópolis donde el sueño está prohibido por decreto municipal.",
        "visibility": Story.Visibility.FULL,
        "tail_words": 5,
        "max_fragments": 3,
        "fragmentos": [
            {
                "author_index": 2,
                "text": (
                    "El Decreto 7 establecía con claridad meridiana que todo ciudadano mayor de doce años "
                    "tenía prohibido cerrar los ojos por más de tres segundos consecutivos entre las ocho "
                    "de la mañana y las dos de la madrugada. Los inspectores del sueño patrullaban en "
                    "silencio, equipados con cronómetros y una lista de sanciones graduales."
                ),
            },
            {
                "author_index": 4,
                "text": (
                    "Sofía había aprendido a soñar con los ojos abiertos. Miraba la pared descascarada "
                    "de su habitación y veía océanos, caballos, la cara de su madre cuando era joven. "
                    "El truco era no parpadear demasiado seguido y mantener una expresión levemente aburrida, "
                    "la misma cara que ponía en las reuniones de trabajo los miércoles."
                ),
            },
            {
                "author_index": 0,
                "text": (
                    "Una noche, sin embargo, todos los inspectores se durmieron al mismo tiempo. "
                    "Nadie supo explicar el fenómeno; algunos dijeron que fue la música que tocó "
                    "una niña en el parque central, otros que fue simplemente el cansancio acumulado "
                    "de años de vigilancia. La ciudad entera cerró los ojos a la vez, y lo que soñó "
                    "colectivamente nunca pudo ser descrito con palabras."
                ),
            },
        ],
    },
    {
        "title": "Tres hermanas y un mapa equivocado",
        "prompt": "Heredan un mapa que lleva al lugar incorrecto, pero perfecto.",
        "visibility": Story.Visibility.TAIL,
        "tail_words": 3,
        "max_fragments": 6,
        "fragmentos": [
            {
                "author_index": 5,
                "text": (
                    "El notario entregó el sobre con cierta vergüenza. «Su tío», dijo, «dejó instrucciones "
                    "muy específicas». Dentro había un mapa dibujado a mano sobre papel de estraza, con "
                    "una X marcada en un lugar que las tres hermanas identificaron de inmediato: "
                    "el estacionamiento del supermercado donde compraban los martes."
                ),
            },
            {
                "author_index": 1,
                "text": (
                    "La hermana mayor, Renata, propuso ignorar el mapa. La del medio, Jimena, propuso "
                    "enmarcarlo. La menor, Paz, propuso seguirlo al pie de la letra, aunque fuera ridículo, "
                    "aunque el tío siempre hubiera sido un hombre de bromas que no hacían gracia. "
                    "Ganó Paz, porque Paz siempre ganaba cuando algo importaba de verdad."
                ),
            },
            {
                "author_index": 3,
                "text": (
                    "Llegaron al estacionamiento un martes, como era costumbre, y en el lugar exacto "
                    "de la X encontraron un carrito de supermercado con una maceta adentro. La maceta "
                    "tenía un geranio rojo y una tarjeta que decía: «Aquí empieza lo bueno». "
                    "Nadie les supo explicar quién había dejado aquello, ni desde cuándo estaba ahí."
                ),
            },
        ],
    },
    {
        "title": "El arquitecto de recuerdos ajenos",
        "prompt": "Un hombre que construye casas a partir de memorias que no son suyas.",
        "visibility": Story.Visibility.FULL,
        "tail_words": 5,
        "max_fragments": 5,
        "fragmentos": [
            {
                "author_index": 4,
                "text": (
                    "Lorenzo no necesitaba planos. Le bastaba con estrechar la mano de sus clientes "
                    "durante exactamente cuatro segundos para saber qué casa necesitaban. No la que "
                    "querían —esa era tarea fácil para cualquier arquitecto— sino la que llevarían "
                    "dentro el resto de sus vidas sin saber que la estaban buscando."
                ),
            },
        ],
    },
    {
        "title": "El último tren a ninguna parte",
        "prompt": "Un tren que parte cada medianoche hacia un destino que cambia cada vez.",
        "visibility": Story.Visibility.TAIL,
        "tail_words": 8,
        "max_fragments": 4,
        "fragmentos": [
            {
                "author_index": 1,
                "text": (
                    "El andén número cero no aparecía en el tablero de salidas. Para encontrarlo "
                    "había que caminar en dirección contraria a los demás pasajeros, doblar a la "
                    "izquierda donde debería haber una pared, y esperar. El tren llegaba puntual "
                    "a las doce en punto, pero nunca era el mismo tren dos veces seguidas."
                ),
            },
            {
                "author_index": 3,
                "text": (
                    "Clara subió sin boleto porque nadie se los pedía. Los otros pasajeros miraban "
                    "por la ventana con expresiones de quien ve algo que no puede explicar pero tampoco "
                    "quiere perderse. El paisaje afuera era distinto al de cualquier trayecto conocido: "
                    "había montañas donde debería haber mar, y el cielo tenía dos lunas o ninguna."
                ),
            },
            {
                "author_index": 5,
                "text": (
                    "A mitad del viaje, el conductor pasó por los vagones repartiendo tazas de té. "
                    "«¿A dónde vamos?», le preguntó Clara. El conductor pensó un momento antes de "
                    "responder: «Esta noche vamos adonde usted necesita ir, no adonde cree que quiere». "
                    "Clara bebió el té, que sabía a lluvia de verano, y no volvió a preguntar."
                ),
            },
            {
                "author_index": 0,
                "text": (
                    "La estación de llegada tenía el nombre de Clara escrito en todas las señales. "
                    "No el nombre que usaba en el trabajo ni el que ponía en los formularios, "
                    "sino el nombre que su abuela le había dado en secreto cuando tenía cinco años "
                    "y que ella creía haber olvidado. Bajó del tren sabiendo exactamente qué hacer a continuación."
                ),
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Poblar la base de datos con datos de prueba realistas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Eliminar los datos seed existentes antes de recrearlos.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        usuarios = self._crear_usuarios()
        self._crear_historias(usuarios)

        self.stdout.write(self.style.SUCCESS("Seed completado exitosamente."))

    def _reset(self):
        emails_seed = [u["email"] for u in USUARIOS]
        usuarios_seed = User.objects.filter(email__in=emails_seed)
        Fragment.objects.filter(author__in=usuarios_seed).delete()
        Story.objects.filter(creator__in=usuarios_seed).delete()
        usuarios_seed.delete()
        self.stdout.write("Datos seed anteriores eliminados.")

    def _crear_usuarios(self):
        usuarios = []
        for datos in USUARIOS:
            usuario, creado = User.objects.get_or_create(
                email=datos["email"],
                defaults={
                    "display_name": datos["display_name"],
                    "bio": datos["bio"],
                },
            )
            if creado:
                self.stdout.write(f"  Usuario creado: {usuario.display_name}")
            usuarios.append(usuario)
        return usuarios

    def _crear_historias(self, usuarios):
        for datos in HISTORIAS:
            historia, creada = Story.objects.get_or_create(
                title=datos["title"],
                defaults={
                    "creator": usuarios[datos["fragmentos"][0]["author_index"]],
                    "prompt": datos["prompt"],
                    "visibility": datos["visibility"],
                    "tail_words": datos["tail_words"],
                    "max_fragments": datos["max_fragments"],
                },
            )
            if creada:
                self.stdout.write(f"  Historia creada: «{historia.title}»")

            for orden, frag_datos in enumerate(datos["fragmentos"], start=1):
                autor = usuarios[frag_datos["author_index"]]
                try:
                    Fragment.objects.create(
                        story=historia,
                        author=autor,
                        text=frag_datos["text"],
                        order=orden,
                    )
                except IntegrityError:
                    pass
