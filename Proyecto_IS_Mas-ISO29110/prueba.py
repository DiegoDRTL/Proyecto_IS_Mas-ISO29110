from alchemyClasses.usuario import create_user

resultado = create_user(
    "Pablo",
    "Huerta",
    "Martinez",
    "1234",
    "2003-05-12",
    "alumno",
    "pablo@test.com",
    "5512345678"
)

if resultado:
    print("Usuario creado correctamente")
else:
    print("Error al crear usuario")