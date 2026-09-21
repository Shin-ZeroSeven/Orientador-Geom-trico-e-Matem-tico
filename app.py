import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="Orientador Geométrico e Matemático", layout="wide", initial_sidebar_state="expanded")

# --- Funções Auxiliares de Matemática e Plotagem ---
def parse_function(expr_str):
    """Converte a string do usuário em uma expressão SymPy."""
    try:
        # Substituições comuns para facilitar a digitação
        expr_str = expr_str.replace('^', '**').replace('e', 'E')
        x = sp.Symbol('x')
        expr = sp.sympify(expr_str)
        return x, expr
    except Exception as e:
        return None, None

def generate_plot(x, expr, x_range=(-10, 10), extra_traces=None, fill_range=None):
    """Gera o gráfico 2D interativo usando Plotly."""
    f_num = sp.lambdify(x, expr, 'numpy')
    x_vals = np.linspace(x_range[0], x_range[1], 800)
    
    # Tratamento para evitar erros com raízes complexas ou assíntotas
    with np.errstate(divide='ignore', invalid='ignore'):
        y_vals = f_num(x_vals)
        if np.iscomplexobj(y_vals):
            y_vals = np.real(np.where(np.isreal(f_num(x_vals + 0j)), y_vals, np.nan))
    
    # Limitação de eixo Y para evitar distorções em assíntotas
    y_vals = np.clip(y_vals, -50, 50)

    fig = go.Figure()

    # Plot da função original
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"f(x) = {sp.latex(expr)}", line=dict(color='#1f77b4', width=2)))

    # Plot da área sombreada (Integral)
    if fill_range:
        a, b = fill_range
        x_fill = np.linspace(float(a), float(b), 200)
        y_fill = f_num(x_fill)
        y_fill = np.clip(y_fill, -50, 50)
        fig.add_trace(go.Scatter(x=x_fill, y=y_fill, fill='tozeroy', mode='none', name='Área (Integral)', fillcolor='rgba(255, 127, 14, 0.3)'))

    # Traços extras (Ex: Reta Tangente)
    if extra_traces:
        for trace in extra_traces:
            y_extra = trace['func'](x_vals)
            y_extra = np.clip(y_extra, -50, 50)
            fig.add_trace(go.Scatter(x=x_vals, y=y_extra, mode='lines', name=trace['name'], line=dict(color=trace['color'], dash=trace.get('dash', 'solid'))))

    fig.update_layout(
        title="Visualização Gráfica",
        xaxis_title="Eixo X",
        yaxis_title="Eixo Y",
        template="plotly_dark",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    # Adicionando Eixos principais
    fig.add_hline(y=0, line_width=1, line_color="gray")
    fig.add_vline(x=0, line_width=1, line_color="gray")
    
    return fig

# --- Interface do Usuário (UI) ---
st.title("📐 Orientador Geométrico e Matemático")
st.markdown("Assistente interativo para análise simbólica, visualização e cálculo passo a passo.")

# Painel Lateral (Inputs)
with st.sidebar:
    st.header("⚙️ Painel de Entrada")
    func_input = st.text_input("Digite a função f(x):", value="x**3 - 3*x + 2")
    st.markdown("*Dicas: Use `**` ou `^` para potências, `sin(x)` para seno, `exp(x)` para exponencial.*")
    
    operation = st.selectbox("Selecione a Operação:", [
        "📈 Análise de Função",
        "📐 Cálculo de Derivada",
        "∫ Cálculo de Integral"
    ])
    
    # Entradas Dinâmicas
    x0, a, b = 0, 0, 0
    if operation == "📐 Cálculo de Derivada":
        x0 = st.number_input("Ponto de avaliação (x0):", value=1.0, step=0.5)
    elif operation == "∫ Cálculo de Integral":
        integral_type = st.radio("Tipo de Integral:", ["Indefinida", "Definida"])
        if integral_type == "Definida":
            col1, col2 = st.columns(2)
            a = col1.number_input("Limite Inferior (a):", value=-1.0, step=0.5)
            b = col2.number_input("Limite Superior (b):", value=2.0, step=0.5)
            
    calcular_btn = st.button("🚀 Calcular e Visualizar", use_container_width=True)

# --- Processamento Principal ---
if calcular_btn:
    x, expr = parse_function(func_input)
    
    if expr is None:
        st.error("Erro ao interpretar a função. Verifique a sintaxe matemática.")
    else:
        st.latex(r"f(x) = " + sp.latex(expr))
        
        # 1. Análise de Função
        if operation == "📈 Análise de Função":
            col_res, col_graf = st.columns([1, 2])
            
            with col_res:
                st.subheader("Resultados Principais")
                # Raízes
                try:
                    roots = sp.solve(expr, x)
                    st.write("**Raízes (f(x) = 0):**")
                    st.latex(sp.latex(roots))
                except:
                    st.write("Raízes: Não foi possível determinar analiticamente.")
                
                # Derivada Primeira (Pontos Críticos)
                f_prime = sp.diff(expr, x)
                try:
                    crit_points = sp.solve(f_prime, x)
                    st.write("**Pontos Críticos (f'(x) = 0):**")
                    st.latex(sp.latex(crit_points))
                except:
                    pass
            
            with col_graf:
                fig = generate_plot(x, expr)
                st.plotly_chart(fig, use_container_width=True)
                
            with st.expander("🔍 Ver Cálculo Detalhado / Passo a Passo"):
                st.markdown("### Passo a Passo: Encontrando Pontos Críticos")
                st.markdown("1. Calcula-se a primeira derivada usando as regras de derivação:")
                st.latex(rf"f'(x) = \frac{{d}}{{dx}}[{sp.latex(expr)}] = {sp.latex(f_prime)}")
                st.markdown("2. Iguala-se a derivada a zero para encontrar extremos locais:")
                st.latex(rf"{sp.latex(f_prime)} = 0 \implies x \in \{{ {sp.latex(crit_points)} \}}")

        # 2. Cálculo de Derivada
        elif operation == "📐 Cálculo de Derivada":
            f_prime = sp.diff(expr, x)
            f_double_prime = sp.diff(expr, x, 2)
            
            # Avaliação no ponto x0
            y0 = expr.subs(x, x0).evalf()
            m = f_prime.subs(x, x0).evalf()
            
            # Equação da Reta Tangente: y - y0 = m(x - x0) -> y = m*(x - x0) + y0
            tangent_expr = m * (x - x0) + y0
            tangent_func = sp.lambdify(x, tangent_expr, 'numpy')
            
            col_res, col_graf = st.columns([1, 2])
            
            with col_res:
                st.subheader("Resultados Principais")
                st.write("**Derivada Primeira f'(x):**")
                st.latex(sp.latex(f_prime))
                st.write("**Derivada Segunda f''(x):**")
                st.latex(sp.latex(f_double_prime))
                st.write(f"**Inclinação em $x_0 = {x0}$:**")
                st.latex(rf"m = {sp.latex(sp.simplify(m))}")
                st.write("**Reta Tangente:**")
                st.latex(rf"y = {sp.latex(sp.simplify(tangent_expr))}")
            
            with col_graf:
                extra = [{'func': tangent_func, 'name': f'Tangente em x={x0}', 'color': '#ff7f0e', 'dash': 'dash'}]
                fig = generate_plot(x, expr, extra_traces=extra)
                st.plotly_chart(fig, use_container_width=True)
                
            with st.expander("🔍 Ver Cálculo Detalhado / Passo a Passo"):
                st.markdown("### Passo a Passo da Reta Tangente")
                st.markdown("1. Obter a coordenada $y_0$ substituindo $x_0$ na função original:")
                st.latex(rf"f({x0}) = {sp.latex(y0)}")
                st.markdown("2. Calcular a primeira derivada da função:")
                st.latex(rf"f'(x) = {sp.latex(f_prime)}")
                st.markdown("3. Avaliar a derivada em $x_0$ para achar a inclinação $m$:")
                st.latex(rf"f'({x0}) = {sp.latex(m)}")
                st.markdown("4. Aplicar na equação da reta ponto-inclinação ($y - y_0 = m(x - x_0)$):")
                st.latex(rf"y - ({sp.latex(y0)}) = {sp.latex(m)} \cdot (x - {x0})")
                st.latex(rf"y = {sp.latex(sp.simplify(tangent_expr))}")

        # 3. Cálculo de Integral
        elif operation == "∫ Cálculo de Integral":
            integral_expr = sp.integrate(expr, x)
            
            col_res, col_graf = st.columns([1, 2])
            
            if integral_type == "Indefinida":
                with col_res:
                    st.subheader("Resultado Principal")
                    st.write("**Integral Indefinida:**")
                    st.latex(rf"\int {sp.latex(expr)} \, dx = {sp.latex(integral_expr)} + C")
                    
                with col_graf:
                    fig = generate_plot(x, expr)
                    st.plotly_chart(fig, use_container_width=True)
                    
                with st.expander("🔍 Ver Cálculo Detalhado / Passo a Passo"):
                    st.markdown("### Passo a Passo da Primitiva")
                    st.markdown("Aplica-se as regras de integração (linearidade, regra da potência, substituição ou partes) conforme a função exige, obtendo a primitiva geral:")
                    st.latex(rf"F(x) = {sp.latex(integral_expr)}")
                    st.markdown("Sempre adicionando a constante de integração $C$ no caso de integrais indefinidas para representar a família de curvas.")

            else:  # Definida
                area_val = sp.integrate(expr, (x, a, b)).evalf()
                
                with col_res:
                    st.subheader("Resultado Principal")
                    st.write("**Integral Definida (Área Exata):**")
                    st.latex(rf"\int_{{{a}}}^{{{b}}} {sp.latex(expr)} \, dx = {sp.latex(sp.simplify(area_val))}")
                    st.write("**Valor Aproximado:**")
                    st.latex(rf"\approx {area_val:.4f}")
                    
                with col_graf:
                    fig = generate_plot(x, expr, fill_range=(a, b))
                    st.plotly_chart(fig, use_container_width=True)
                    
                with st.expander("🔍 Ver Cálculo Detalhado / Passo a Passo"):
                    st.markdown("### Passo a Passo: Teorema Fundamental do Cálculo")
                    st.markdown("1. Encontra-se a primitiva geral da função:")
                    st.latex(rf"\int {sp.latex(expr)} \, dx = {sp.latex(integral_expr)}")
                    st.markdown("2. Avalia-se a primitiva no limite superior $b$:")
                    Fa = integral_expr.subs(x, a).evalf()
                    Fb = integral_expr.subs(x, b).evalf()
                    st.latex(rf"F({b}) = {sp.latex(Fb)}")
                    st.markdown("3. Avalia-se a primitiva no limite inferior $a$:")
                    st.latex(rf"F({a}) = {sp.latex(Fa)}")
                    st.markdown("4. Calcula-se a diferença $F(b) - F(a)$:")
                    st.latex(rf"\int_{{{a}}}^{{{b}}} f(x) \, dx = {sp.latex(Fb)} - ({sp.latex(Fa)}) = {sp.latex(sp.simplify(area_val))}")
