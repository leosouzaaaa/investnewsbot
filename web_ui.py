import streamlit as st
from app.auth import verify_user, init_db
from app.analyzer import generate_suggestions
from app.config import STOCKS, CRYPTOS
st.set_page_config(page_title='Invest Bot', layout='wide')
if 'logged_in' not in st.session_state: st.session_state['logged_in']=False
if not st.session_state['logged_in']:
    st.header('Login')
    username = st.text_input('Usuário')
    password = st.text_input('Senha', type='password')
    if st.button('Entrar'):
        user = verify_user(username, password)
        if user:
            st.session_state['logged_in']=True; st.session_state['user']=user; st.experimental_rerun()
        else:
            st.error('Usuário ou senha incorretos')
else:
    st.sidebar.write(f"Logado como: {st.session_state['user']['full_name']}")
    if st.sidebar.button('Sair'): st.session_state['logged_in']=False; st.experimental_rerun()
    st.title('Invest Bot — Dashboard')
    if st.button('Atualizar recomendações agora'):
        suggestions = generate_suggestions(STOCKS, CRYPTOS)
        st.session_state['last_suggestions']=suggestions
    if 'last_suggestions' in st.session_state:
        s = st.session_state['last_suggestions']
        st.subheader('Daily'); st.table(s['daily'])
        st.subheader('Weekly'); st.table(s['weekly'])
        st.subheader('Monthly'); st.table(s['monthly'])
