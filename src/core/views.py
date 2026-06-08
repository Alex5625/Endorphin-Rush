from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, TipoEjercicio
from .forms import RegistroCompletoForm, EditarPerfilForm , TipoEjercicioForm
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.cache import never_cache

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():
            # Guardar el usuario primero para obtener su instancia y luego crear el perfil asociado
            usuario_nuevo = form.save()
            
            # Crear el perfil asociado al usuario con los datos adicionales del formulario
            perfil = PerfilUsuario.objects.create(
                usuario=usuario_nuevo,
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                edad=form.cleaned_data['edad'],
                sexo=form.cleaned_data['sexo'],
                peso=form.cleaned_data['peso'],
                altura=form.cleaned_data['altura']
            )
            correo_destino = form.cleaned_data['username']
            enviar_correo(perfil, correo_destino)
            
            #Entregar el mensaje flotante
            messages.success(
                request, 
                f"¡Registro completado con éxito, {perfil.nombre}! Te hemos enviado un correo de confirmación con tu información ingresada."
            )
            # Logueo automatico después de registrarse
            login(request, usuario_nuevo)
            
            return redirect('home') # Te manda al inicio ya con tu cuenta lista
    else:
        form = RegistroCompletoForm()
        
    return render(request, 'core/registro.html', {'form': form})

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
            form.save() 
            
            # 4. Encolamos el mensaje flotante de éxito
            messages.success(request, "¡Tus datos corporales se han actualizado correctamente!")
            
            return redirect('home')
    else:
        # Petición GET: Carga el formulario relleno con los datos viejos de la BD
        form = EditarPerfilForm(instance=perfil)
        
    return render(request, 'core/editar_perfil.html', {'form': form})

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
        return redirect('login')
    
    return redirect('login')

#vistas para el entrenador: gestion de tipos de ejercicio
#hu-29 permite al entrenador visualizar la lista de categorias musculares 
#y agregar una nueva en la misma pantalla

def gestion_tipos_ejercicio(request):

    categorias = TipoEjercicio.objects.all().order_by('nombre_categoria')
    
    if request.method== 'POST':
        form = TipoEjercicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo muscular agregado exitosamente!")
            return redirect('gestion_tipos_ejercicio')
        
    else:
        form = TipoEjercicioForm()

    context = {
        'categorias': categorias,
        'form': form
    }
    return render(request, 'core/gestion_tipos.html', context)

#hu-30 permite al entrenador modificar el nombre de un grupo muscular existente
def editar_tipo_ejercicio(request, pk):
    
    categoria = get_object_or_404(TipoEjercicio, pk=pk)

    if request.method == 'POST':
        form = TipoEjercicioForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo muscular actualizado exitosamente!")
            return redirect('gestion_tipos_ejercicio')
        
    else:
        form= TipoEjercicioForm(instance=categoria)

    return render(request, 'core/editar_tipo.html', {'form': form, 'categoria': categoria})

#HU-31 permite al entrenador eliminar un grupo muscular en forma directa.
def eliminar_tipo_ejercicio(request, pk):
    
    categoria = get_object_or_404(TipoEjercicio, pk=pk)
    nombre = categoria.nombre_categoria
    categoria.delete()
    messages.success(request, f"El grupo muscular '{nombre}' ha sido eliminado exitosamente.")
    return redirect('gestion_tipos_ejercicio')
