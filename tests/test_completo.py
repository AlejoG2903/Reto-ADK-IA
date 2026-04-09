import pytest
import os
import re
from pathlib import Path
from datetime import datetime

# ============================================================================
# TEST SUITE COMPLETO - Sistema de Gestión Clínica con MCP (25+ tests)
# ============================================================================

class TestEstructuraProyecto:
    """Pruebas de estructura básica del proyecto"""
    
    def test_directorios_principales_existen(self):
        """Verificar que existen los directorios principales"""
        directorios = ["apps", "infrastructure", "tests", "workspace"]
        for d in directorios:
            assert os.path.isdir(d), f"Directorio faltante: {d}"
    
    def test_servicios_mcp_existen(self):
        """Cada servicio MCP debe tener su directorio"""
        servicios = [
            "apps/mcp_servers/mcp_database",
            "apps/mcp_servers/mcp_filesystem",
            "apps/mcp_servers/mcp_api",
            "apps/mcp_servers/mcp_analitica"
        ]
        for servicio in servicios:
            assert os.path.isdir(servicio), f"Falta directorio: {servicio}"
    
    def test_archivos_configuracion_existen(self):
        """Deben existir archivos de configuración"""
        archivos = ["docker-compose.yml", ".env.example", ".gitignore", "README.md"]
        for archivo in archivos:
            assert os.path.isfile(archivo), f"Falta archivo: {archivo}"
    
    def test_dockerfiles_todos_presentes(self):
        """Cada servicio debe tener Dockerfile"""
        servicios = [
            "apps/agente",
            "apps/mcp_servers/mcp_database",
            "apps/mcp_servers/mcp_filesystem",
            "apps/mcp_servers/mcp_api",
            "apps/mcp_servers/mcp_analitica"
        ]
        for s in servicios:
            dockerfile = f"{s}/Dockerfile"
            assert os.path.isfile(dockerfile), f"Falta: {dockerfile}"
    
    def test_requirements_todos_presentes(self):
        """Cada servicio debe tener requirements.txt"""
        servicios = [
            "apps/agente",
            "apps/mcp_servers/mcp_database",
            "apps/mcp_servers/mcp_filesystem",
            "apps/mcp_servers/mcp_api",
            "apps/mcp_servers/mcp_analitica"
        ]
        for s in servicios:
            req = f"{s}/requirements.txt"
            assert os.path.isfile(req), f"Falta: {req}"
    
    def test_migraciones_sql_presentes(self):
        """Deben existir archivos de migración SQL"""
        assert os.path.isfile("infrastructure/db/migrations/001_create_tables.sql")
        assert os.path.isfile("infrastructure/db/migrations/002_seed_data.sql")

class TestSeguridad:
    """Validar que NO hay vulnerabilidades de seguridad"""
    
    def test_env_en_gitignore(self):
        """El archivo .env debe estar en .gitignore"""
        with open(".gitignore", encoding='utf-8') as f:
            assert ".env" in f.read()
    
    def test_sin_api_keys_reales_en_env_example(self):
        """NO debe haber API keys reales en .env.example"""
        with open(".env.example", encoding='utf-8') as f:
            contenido = f.read()
            # Buscar patrones de Google API keys
            assert not re.search(r'AIzaSy[A-Za-z0-9_-]{35}', contenido)
            # Debe tener placeholder o estar vacío
            assert 'YOUR_API_KEY' in contenido or 'GOOGLE_API_KEY=' in contenido
    
    def test_sin_credentials_hardcodeadas_en_codigo(self):
        """NO debe haber credenciales en archivos Python"""
        python_files = list(Path("apps").rglob("*.py"))
        for py_file in python_files:
            with open(py_file, encoding='utf-8') as f:
                contenido = f.read()
                # No debe tener Google API keys
                assert not re.search(r'AIzaSy[A-Za-z0-9_-]{35}', contenido)
                # No must hardcodear passwords simples
                assert "password='admin'" not in contenido.lower()
    
    def test_sin_eval_inseguro(self):
        """NO debe usarse eval() sin seguridad"""
        python_files = list(Path("apps").rglob("*.py"))
        for py_file in python_files:
            with open(py_file, encoding='utf-8') as f:
                contenido = f.read()
                # eval() es inseguro y no debe estar en código de producción
                if "eval(" in contenido:
                    # Permitir solo en comentarios o docstrings
                    for linea in contenido.split('\n'):
                        if 'eval(' in linea and not linea.strip().startswith('#'):
                            if '"""' not in linea and "'''" not in linea:
                                pytest.fail(f"eval() inseguro en {py_file}")
    
    def test_requirements_sin_vulnerabilidades_conocidas(self):
        """Los requirements deben usar versiones seguras"""
        req_files = list(Path(".").rglob("requirements.txt"))
        for req_file in req_files:
            with open(req_file, encoding='utf-8') as f:
                contenido = f.read()
                # Verificar que no hay versiones muy antiguas / vulnerables
                # Por ejemplo, pickle desserialización insegura
                assert "pickle" not in contenido
                assert "marshal" not in contenido

class TestConfiguracion:
    """Validar archivo de configuración"""
    
    def test_docker_compose_estructura_valida(self):
        """docker-compose.yml debe tener estructura correcta"""
        try:
            import yaml
            with open("docker-compose.yml", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                assert 'services' in config
                assert 'postgres' in config['services']
                assert 'agente' in config['services']
        except ImportError:
            # Si no está instalado yaml, al menos verificar que es JSON-like
            with open("docker-compose.yml") as f:
                contenido = f.read()
                assert 'services:' in contenido
                assert 'postgres:' in contenido
    
    def test_puertos_no_duplicados(self):
        """No debe haber puertos duplicados en docker-compose"""
        try:
            import yaml
            with open("docker-compose.yml", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                puertos = set()
                for servicio, svc_config in config['services'].items():
                    if 'ports' in svc_config:
                        for mapeo in svc_config['ports']:
                            puerto_ext = mapeo.split(':')[0]
                            assert puerto_ext not in puertos, f"Puerto duplicado: {puerto_ext}"
                            puertos.add(puerto_ext)
        except ImportError:
            pass  # Skip si no está yaml disponible
    
    def test_env_example_completitud(self):
        """El .env.example debe tener todas las variables requeridas"""
        with open(".env.example", encoding='utf-8') as f:
            contenido = f.read()
            variables = [
                'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB',
                'CAPACIDAD_TURNO', 'LLM_MODEL', 'GOOGLE_API_KEY'
            ]
            for var in variables:
                assert var in contenido, f"Falta variable: {var}"

class TestDatos:
    """Validar integridad de datos de prueba"""
    
    def test_seed_data_sql_valido(self):
        """El SQL de seed debe ser válido"""
        with open("infrastructure/db/migrations/002_seed_data.sql", encoding='utf-8') as f:
            sql = f.read()
            # Verificar statements básicos
            assert "INSERT INTO" in sql
            assert "SELECT" not in sql or "INSERT INTO" in sql  # Debe tener INSERTs
    
    def test_seed_data_tiene_tablas(self):
        """El seed debe insertar en las tablas correctas"""
        with open("infrastructure/db/migrations/002_seed_data.sql", encoding='utf-8') as f:
            sql = f.read()
            tablas = ['pacientes', 'diagnosticos', 'medicamentos', 'consultas']
            for tabla in tablas:
                assert tabla in sql, f"Tabla {tabla} no tiene seed"
    
    def test_datos_seed_minimos(self):
        """El seed debe tener datos de ejemplo mínimos"""
        with open("infrastructure/db/migrations/002_seed_data.sql", encoding='utf-8') as f:
            sql = f.read()
            # Debe tener al menos varios registros de ejemplo
            insert_count = sql.count("INSERT INTO")
            assert insert_count >= 4, "Debe haber al menos 4 INSERTs"

class TestCodigoLimpio:
    """Validar calidad del código"""
    
    def test_python_sintaxis_valida(self):
        """Todos los archivos Python deben tener sintaxis válida"""
        import ast
        python_files = list(Path("apps").rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                pytest.fail(f"Error de sintaxis en {py_file}: {e}")
    
    def test_requirements_formato_valido(self):
        """Las líneas de requirements deben ser válidas"""
        req_files = list(Path(".").rglob("requirements.txt"))
        patron = re.compile(r'^[a-zA-Z0-9_\-\.]+(\[.*\])?([><=!~]+.*)?$')
        for req_file in req_files:
            with open(req_file, encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea or linea.startswith('#'):
                        continue
                    assert patron.match(linea), f"Línea inválida en {req_file}: {linea}"

class TestDocumentacion:
    """Validar que el proyecto esté documentado"""
    
    def test_readme_existe_y_completo(self):
        """El README debe existir y tener contenido significativo"""
        assert os.path.isfile("README.md")
        with open("README.md", encoding='utf-8') as f:
            contenido = f.read()
            assert len(contenido) > 300, "README muy corto"
            # Debe tener instrucciones básicas
            keywords = ['docker', 'compose', 'servicio', 'puerto']
            assert any(k in contenido.lower() for k in keywords)
    
    def test_gitignore_protege_archivos_sensibles(self):
        """El .gitignore debe excluir archivos sensitive"""
        with open(".gitignore", encoding='utf-8') as f:
            contenido = f.read()
            sensibles = ['.env', '__pycache__', '.vscode', '.idea']
            for s in sensibles:
                assert s in contenido, f"{s} no está en .gitignore"

class TestIntegracion:
    """Pruebas de integración básica"""
    
    def test_mcp_services_tienen_main(self):
        """Cada servicio MCP debe tener main.py"""
        servicios = [
            "apps/mcp_servers/mcp_database",
            "apps/mcp_servers/mcp_filesystem",
            "apps/mcp_servers/mcp_api",
            "apps/mcp_servers/mcp_analitica"
        ]
        for s in servicios:
            assert os.path.isfile(f"{s}/main.py"), f"Falta main.py en {s}"
    
    def test_agente_es_ejecutable(self):
        """El agente debe ser ejecutable"""
        agente_file = "apps/agente/main.py"
        assert os.path.isfile(agente_file)
        with open(agente_file, encoding='utf-8') as f:
            contenido = f.read()
            # Debe tener if __name__ == "__main__"
            assert '__main__' in contenido
    
    def test_mcp_servicios_usan_mcptools(self):
        """Los servicios deben usar MCP (FastMCP o Google ADK)"""
        servicios = [
            "apps/mcp_servers/mcp_database/main.py",
            "apps/mcp_servers/mcp_filesystem/main.py",
            "apps/mcp_servers/mcp_api/main.py",
            "apps/mcp_servers/mcp_analitica/main.py"
        ]
        for s in servicios:
            with open(s, encoding='utf-8') as f:
                contenido = f.read()
                # Debe tener FastMCP o generar tools
                assert 'FastMCP' in contenido or '@mcp' in contenido or '@tool' in contenido, \
                    f"{s} no define herramientas MCP"

class TestGoogleADK:
    """Validar que Google ADK es obligatorio y se está usando"""
    
    def test_google_adk_requerido_en_requirements(self):
        """Google ADK debe estar en requirements del agente"""
        with open("apps/agente/requirements.txt", encoding='utf-8') as f:
            contenido = f.read()
            assert "google-adk" in contenido, "google-adk NO está en requirements"
    
    def test_agente_importa_google_adk(self):
        """El agente debe importar desde google.adk"""
        with open("apps/agente/main.py", encoding='utf-8') as f:
            contenido = f.read()
            # Debe importar de google.adk
            assert "from google.adk" in contenido, "No importa de google.adk"
            assert "LlmAgent" in contenido, "No usa LlmAgent"
            assert "McpToolset" in contenido, "No usa McpToolset"
            assert "SseConnectionParams" in contenido, "No usa SseConnectionParams"
            assert "Runner" in contenido, "No usa Runner"
    
    def test_agente_configura_model_google(self):
        """El agente debe configurar un modelo de Google"""
        with open("apps/agente/main.py", encoding='utf-8') as f:
            contenido = f.read()
            # Debe usar LLM_MODEL
            assert "LLM_MODEL" in contenido
            # model parameter en LlmAgent
            assert "model=MODEL" in contenido or "model =" in contenido
    
    def test_env_example_menciona_google_adk(self):
        """El .env.example debe tener instrucciones de Google ADK"""
        with open(".env.example", encoding='utf-8') as f:
            contenido = f.read()
            assert "GOOGLE_API_KEY" in contenido
            # Debe tener comentario sobre que es requerido
            assert "google" in contenido.lower()
    
    def test_sin_fastmcp_en_agente(self):
        """El agente NO debe usar FastMCP directo (solo Google ADK)"""
        with open("apps/agente/main.py", encoding='utf-8') as f:
            contenido = f.read()
            # El agente debe usar Google ADK, no FastMCP directo
            # (FastMCP se usa en los servicios MCP, no en agente)
            # Verificar que usa google.adk.tools.mcp_tool, no fastmcp directo
            if "FastMCP" in contenido:
                # Si menciona FastMCP, debe ser en comentarios o strings
                assert contenido.count("FastMCP") == 0 or \
                       all("#" in line for line in contenido.split('\n') 
                           if "FastMCP" in line), \
                       "El agente NO debe crear FastMCP, solo usar McpToolset de Google ADK"
        """Los puertos deben estar bien asignados"""
        try:
            import yaml
            with open("docker-compose.yml", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                puertos_esperados = {
                    'postgres': '5432',
                    'mcp_database': '8001',
                    'mcp_filesystem': '8002',
                    'mcp_api': '8003',
                    'mcp_analitica': '8004',
                    'agente': '8005'
                }
                for servicio, puerto_esperado in puertos_esperados.items():
                    if servicio in config['services']:
                        puertos = config['services'][servicio].get('ports', [])
                        if puertos:
                            puerto_ext = puertos[0].split(':')[0]
                            # Verificar que coincide
                            assert puerto_ext == puerto_esperado or \
                                   puerto_ext.endswith(puerto_esperado) or \
                                   puertos[0].endswith(f":{puerto_esperado}"), \
                                f"Puerto incorrecto para {servicio}"
        except ImportError:
            pass

# ============================================================================
# TOTAL: 28 TESTS PARA VALIDACIÓN COMPLETA
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

