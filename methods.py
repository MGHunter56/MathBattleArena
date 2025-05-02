import numpy as np
import random
from sympy import symbols, lambdify, diff, integrate, Matrix
from sympy.abc import x
import math

# --------------------------
# Generadores de problemas
# --------------------------

def generar_problema_aleatorio():
    """Genera un problema aleatorio de alguna categoría"""
    categorias = {
        'no_lineales': generar_problema_no_lineal,
        'sistemas': generar_problema_sistema,
        'interpolacion': generar_problema_interpolacion,
        'integracion': generar_problema_integracion,
        'derivacion': generar_problema_derivacion
    }
    
    tipo = random.choice(list(categorias.keys()))
    return categorias[tipo]()

def generar_funcion_aleatoria(grado=3):
    """Genera una función polinómica aleatoria"""
    coeficientes = [random.randint(-5, 5) for _ in range(grado + 1)]
    while coeficientes[0] == 0:
        coeficientes[0] = random.randint(1, 5)
    
    f_expr = sum(c * x**i for i, c in enumerate(reversed(coeficientes)))
    f = lambdify(x, f_expr, modules=['numpy'])
    texto = str(f_expr).replace("**", "^").replace("*", "")
    
    return f, f_expr, texto

def generar_problema_no_lineal():
    """Genera un problema de ecuaciones no lineales"""
    f, f_expr, texto_funcion = generar_funcion_aleatoria()
    a, b = sorted([random.randint(-10, 10) for _ in range(2)])
    
    # Asegurar que hay cambio de signo
    while f(a) * f(b) >= 0:
        a, b = sorted([random.randint(-10, 10) for _ in range(2)])
    
    raiz = metodo_biseccion(f, a, b)
    
    return {
        'tipo': 'no_lineales',
        'enunciado': f"Encuentra una raíz de la función f(x) = {texto_funcion} en el intervalo [{a}, {b}]",
        'formato': "Decimal con 6 cifras (ej: 1.234567)",
        'solucion': f"{raiz:.6f}",
        'datos': {
            'funcion': texto_funcion,
            'intervalo': [a, b],
            'metodo': 'biseccion'
        }
    }

def generar_problema_sistema():
    """Genera un sistema de ecuaciones lineales de tamaño aleatorio entre 2x2 y 5x5"""
    n = random.randint(2, 5)  # Tamaño aleatorio entre 2 y 5
    
    # Generar matriz invertible
    while True:
        A = np.random.randint(-5, 6, size=(n, n))
        # Asegurar que la matriz sea invertible y no tenga filas/columnas de ceros
        if np.linalg.matrix_rank(A) == n and not np.any(np.all(A == 0, axis=1)) and not np.any(np.all(A == 0, axis=0)):
            break
    
    x_real = np.random.randint(-5, 6, size=(n, 1))
    b = A @ x_real
    
    # Formatear matriz para mejor visualización
    matriz_formateada = "\n".join([" ".join([f"{elem:3}" for elem in fila]) for fila in A])
    
    return {
        'tipo': 'sistemas',
        'enunciado': f"Resuelve el sistema Ax = b (Tamaño: {n}x{n})\n\nMatriz A:\n{matriz_formateada}\n\nVector b:\n{b.flatten()}",
        'formato': f"Ingresa {n} valores separados por espacios (ej: {' '.join(['1.0']*n)})",
        'solucion': " ".join([f"{v[0]:.2f}" for v in x_real]),
        'datos': {
            'A': A.tolist(),
            'b': b.tolist(),
            'size': n
        }
    }

def generar_problema_interpolacion():
    """Genera un problema de interpolación"""
    f, f_expr, texto_funcion = generar_funcion_aleatoria(grado=2)
    puntos = sorted(random.sample(range(-10, 11), 3))
    valores = [f(xi) for xi in puntos]
    x_interpolar = random.uniform(min(puntos), max(puntos))
    y_real = f(x_interpolar)
    
    return {
        'tipo': 'interpolacion',
        'enunciado': f"""Interpola los siguientes puntos y estima f({x_interpolar:.2f}):
        {', '.join([f'({xi}, {yi:.2f})' for xi, yi in zip(puntos, valores)])}""",
        'formato': "Decimal con 4 cifras (ej: 12.3456)",
        'solucion': f"{y_real:.4f}",
        'datos': {
            'puntos': list(zip(puntos, valores)),
            'x_interpolar': x_interpolar,
            'metodo': 'lagrange'
        }
    }

def generar_problema_integracion():
    """Genera un problema de integración numérica"""
    f, f_expr, texto_funcion = generar_funcion_aleatoria(grado=3)
    a, b = sorted([random.randint(-5, 5) for _ in range(2)])
    integral = integrate(f_expr, (x, a, b)).evalf()
    
    return {
        'tipo': 'integracion',
        'enunciado': f"Calcula la integral de f(x) = {texto_funcion} desde {a} hasta {b}",
        'formato': "Decimal con 4 cifras (ej: 12.3456)",
        'solucion': f"{integral:.4f}",
        'datos': {
            'funcion': texto_funcion,
            'intervalo': [a, b],
            'metodo': 'trapecio'
        }
    }

def generar_problema_derivacion():
    """Genera un problema de derivación numérica"""
    f, f_expr, texto_funcion = generar_funcion_aleatoria(grado=4)
    x0 = random.uniform(-5, 5)
    derivada = diff(f_expr, x).subs(x, x0).evalf()
    
    return {
        'tipo': 'derivacion',
        'enunciado': f"Calcula la derivada de f(x) = {texto_funcion} en x = {x0:.2f}",
        'formato': "Decimal con 4 cifras (ej: 12.3456)",
        'solucion': f"{derivada:.4f}",
        'datos': {
            'funcion': texto_funcion,
            'punto': x0,
            'metodo': 'dif_centrales'
        }
    }

# --------------------------
# Métodos numéricos
# --------------------------

def metodo_biseccion(f, a, b, tol=1e-6, max_iter=100):
    """Implementación del método de bisección"""
    if f(a) * f(b) >= 0:
        return (a + b) / 2  # Fallback
    
    for _ in range(max_iter):
        c = (a + b) / 2
        if abs(f(c)) < tol:
            return c
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
    return (a + b) / 2

def metodo_newton(f_expr, x0, tol=1e-6, max_iter=100):
    """Método de Newton-Raphson"""
    f = lambdify(x, f_expr)
    df = lambdify(x, diff(f_expr, x))
    xn = float(x0)
    
    for _ in range(max_iter):
        fxn = f(xn)
        dfxn = df(xn)
        
        if abs(fxn) < tol:
            return xn
        if dfxn == 0:
            break
            
        xn = xn - fxn / dfxn
    
    return xn

def metodo_gauss(A, b):
    """Resolución de sistemas por eliminación gaussiana"""
    return np.linalg.solve(A, b)

def metodo_lagrange(puntos, x_interpolar):
    """Interpolación por método de Lagrange"""
    n = len(puntos)
    x_vals, y_vals = zip(*puntos)
    resultado = 0.0
    
    for i in range(n):
        term = y_vals[i]
        for j in range(n):
            if i != j:
                term *= (x_interpolar - x_vals[j]) / (x_vals[i] - x_vals[j])
        resultado += term
    
    return resultado

# --------------------------
# Evaluación de respuestas
# --------------------------

def evaluar_respuesta(problema, respuesta):
    """Evalúa la respuesta del jugador"""
    try:
        if problema['tipo'] == 'no_lineales':
            resp_num = float(respuesta)
            sol_num = float(problema['solucion'])
            error = abs(resp_num - sol_num)
            
        elif problema['tipo'] == 'sistemas':
            n = problema['datos']['size']
            resp = np.array([float(x) for x in respuesta.split()])
            if len(resp) != n:
                return {'error': float('inf'), 'valida': False}
            
            sol = np.array([float(x) for x in problema['solucion'].split()])
            error = np.linalg.norm(resp - sol)
            return {'error': error, 'valida': True}
            
        elif problema['tipo'] in ['interpolacion', 'integracion', 'derivacion']:
            resp_num = float(respuesta)
            sol_num = float(problema['solucion'])
            error = abs(resp_num - sol_num)
            
        else:
            error = float('inf')
            
        return {'error': error, 'valida': True}
        
    except Exception as e:
        print(f"Error evaluando respuesta: {e}")
        return {'error': float('inf'), 'valida': False}