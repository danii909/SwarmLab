from __future__ import annotations
from pathlib import Path
import streamlit as st

def render_global_sidebar():
    with st.sidebar:
        st.header("⚙️ Configurazione globale")
        st.divider()

        st.subheader("📁 Istanza")
        map_dir = Path("docs") / "Mappa"
        instances_found = sorted(
            str(p) for p in map_dir.glob("*.json")
        )
        if not instances_found:
            instances_found = [str(map_dir / "A.json"), str(map_dir / "B.json")]

        instances_found = [p for p in instances_found if Path(p).exists()] or instances_found
        instance_path = st.selectbox("File istanza", options=instances_found, index=0)

        st.subheader("⚙️ Seed")
        seed = st.number_input("(−1 = casuale)", min_value=-1, max_value=9999, value=42)

        st.markdown(
            """
            <style>
                /* Forza il contenitore della sidebar a occupare tutto lo spazio verticale */
                [data-testid="stSidebarUserContent"] {
                    display: flex;
                    flex-direction: column;
                    height: 95vh;
                }

                /* Spinge l'ultimo elemento (il footer) in fondo */
                .mini-footer-container {
                    margin-top: auto;
                    padding-bottom: 20px;
                }

                .mini-footer {
                    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
                    border-radius: 12px;
                    padding: 12px;
                    border: 1px solid rgba(255,255,255,0.1);
                    text-align: center;
                    transition: 0.3s;
                }
                
                .mini-footer:hover {
                    border-color: #ff4b4b;
                    background: rgba(255, 75, 75, 0.05);
                }

                .footer-tag {
                    font-size: 10px;
                    text-transform: uppercase;
                    letter-spacing: 1.2px;
                    color: #808495;
                    margin-bottom: 4px;
                }

                .footer-name {
                    font-size: 16px;
                    font-weight: 700;
                    color: #ffffff;
                    margin-bottom: 10px;
                    display: block;
                }

                .github-mini-btn {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    background-color: #262730;
                    color: #ffffff !important;
                    text-decoration: none;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    border: 1px solid rgba(255,255,255,0.2);
                    transition: 0.2s;
                }

                .github-mini-btn:hover {
                    background-color: #ff4b4b;
                    border-color: #ff4b4b;
                    transform: scale(1.05);
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # --- MINI PREMIUM FOOTER RACCHIUSO NEL CONTAINER ---
        st.markdown(
            """
            <div class="mini-footer-container">
                <div class="mini-footer">
                    <div class="footer-tag">Developer</div>
                    <span class="footer-name">Daniele Barbagallo</span>
                    <a class="github-mini-btn" href="https://github.com/danii909" target="_blank">
                        <svg height="14" width="14" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/>
                        </svg>
                        danii909
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    return instance_path, seed