from django.shortcuts import render
from .models import PerfilUsuario
from core.models import HistorialAcciones, TerminosCondiciones
from .forms import RegistroCompletoForm, EditarPerfilForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import Group

# Create your views here.


def registrar_usuario(request):
    # print(request.method)
    if request.method == 'POST':
        # print(request.POST)
        form = RegistroCompletoForm(request.POST)
        
        if form.is_valid():
            # Guardar el usuario primero para obtener su instancia y luego crear el perfil asociado
            # print("\n🚀 1. ¡EL FORMULARIO ES VÁLIDO! Iniciando guardado...")
            usuario_nuevo = form.save()

            # Le asignamos la etiqueta de Gymbro al usuario que acaba de guardarse
            grupo_gymbro, creado = Group.objects.get_or_create(name='Gymbro')
            usuario_nuevo.groups.add(grupo_gymbro)
            
            # print(f"👤 2. Usuario creado en Auth: {usuario_nuevo.username} (ID: {usuario_nuevo.id})")
            # Crear el perfil asociado al usuario con los datos adicionales del formulario
            perfil = PerfilUsuario.objects.create(
                usuario=usuario_nuevo,
                nombre=form.cleaned_data['first_name'],  # Usamos el campo first_name del User para el nombre
                apellido=form.cleaned_data['last_name'],  # Usamos el campo last_name del User para el apellido
                edad=form.cleaned_data['edad'],
                sexo=form.cleaned_data['sexo'],
                peso=form.cleaned_data['peso'],
                altura=form.cleaned_data['altura']
            )
            # print(f"📊 3. Perfil vinculado creado para: {perfil.nombre} {perfil.apellido}")
            correo_destino = usuario_nuevo.email
            # print(f"📧 4. Intentando enviar correo a: {correo_destino}")
            enviar_correo(perfil, correo_destino)
            # print("✉️ 5. Función enviar_correo ejecutada.")

            #para el historial
            HistorialAcciones.objects.create(
                usuario=usuario_nuevo,
                accion="Creación de cuenta",
                detalle=f"El usuario {usuario_nuevo.username} ({perfil.nombre} {perfil.apellido}) se ha registrado en el sistema."
            )
            # print(f"📝 6. Historial de acciones actualizado para: {usuario_nuevo.username}")

            #Entregar el mensaje flotante
            messages.success(
                request, 
                f"¡Registro completado con éxito, {perfil.nombre}! Te hemos enviado un correo de confirmación con tu información ingresada."
            )
            # Logueo automatico después de registrarse
            # print(f"🔐 7. Intentando loguear al nuevo usuario: {usuario_nuevo.username}")
            login(request, usuario_nuevo)
            # print(f"✅ 8. Usuario logueado: {request.user.username}")
            # print("🚀 9. Redirigiendo al inicio...")
            return redirect('core:home') # Te manda al inicio ya con tu cuenta lista
        # else:
        #     # 🚨 ESTO IMPRIMIRÁ EL ERROR REAL EN TU TERMINAL DE UNIX/WSL
        #     print("\n" + "="*50)
        #     print("ERRORES DETECTADOS POR DJANGO:")
        #     print(form.errors.as_data())
        #     print("="*50 + "\n")
    else:
        form = RegistroCompletoForm()
        # Buscamos el texto legal activo
    terminos = TerminosCondiciones.objects.first()

    return render(request, 'authentication/registro.html', {'form': form, 'terminos': terminos})


def enviar_correo(perfil, correo_destino):
    asunto = "¡Confirmación de Registro - Endorphin Rush!"
    mensaje = f"""
    Hola {perfil.nombre} {perfil.apellido},

    ¡Tu cuenta ha sido creada con éxito en Endorphin Rush!
    
    A continuacion te entregamos el resumen de los datos fisicos que digitaste:
    --------------------------------------------------
    - Edad: {perfil.edad} anios
    - Sexo: {perfil.sexo}
    - Peso Corporal: {perfil.peso} kg
    - Estatura: {perfil.altura} m
    --------------------------------------------------
    
    Ya puedes iniciar sesion y comenzar a registrar tus entrenamientos.
    
    Atentamente,
    El equipo de Endorphin Rush.
    """
    
    send_mail(
                subject=asunto,
                message=mensaje,
                from_email=None, # Usa el DEFAULT_FROM_EMAIL que pusimos en settings
                recipient_list=[correo_destino], # Lista de destinatarios
                fail_silently=False, # Si el correo falla, arrojará un error en la app para enterarnos
            )

@login_required
@never_cache
def editar_perfil(request):
    # La funcion get_or_create busca bien en la base de datos, pero si entra por ejemplo el admin sin tener un perfil creado, lo crea automáticamente con datos por defecto para evitar errores en la app. 
    # De esta forma, siempre habrá un perfil asociado al usuario.
    perfil, created = PerfilUsuario.objects.get_or_create(
            usuario=request.user,
            defaults={
                'nombre': request.user.first_name or "Usuario",
                'apellido': request.user.last_name or "Administrador",
                'edad': 25,
                'sexo': 'O',
                'peso': 70.0,
                'altura': 1.70
            }
        )
    # 1. Obtenemos el perfil del usuario que tiene la sesión activa
    #perfil = request.user.perfil 
    
    if request.method == 'POST':
        # 2. Le pasamos los datos del POST pero vinculados a la instancia actual
        form = EditarPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            # 3. Guarda los cambios directamente sobre el mismo registro en la BD
            perfil_editado = form.save() 

            #para el historial
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion="Modificación de perfil",
                detalle=f"El usuario actualizó sus datos de perfil o contacto (Correo: {request.user.email})."
            )
            
            # 4. Encolamos el mensaje flotante de éxito
            messages.success(request, "¡Tus datos corporales se han actualizado correctamente!")
            
            return redirect('core:home')
    else:
        # Petición GET: Carga el formulario relleno con los datos viejos de la BD
        form = EditarPerfilForm(instance=perfil)
        
    return render(request, 'authentication/editar_perfil.html', {'form': form})

@login_required
def eliminar_perfil(request):
    if request.method == 'POST':
        user = request.user
        
        
        # Desactivación de la cuenta
        user.is_active = False
        user.save() 
        #Cierre de sesión 
        logout(request) 
        
        #Redirección directa al login
        return redirect('authentication:login')
    
    return redirect('authentication:login')

