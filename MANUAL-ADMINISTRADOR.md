/* ==========================================================================
   TERRAE — admin.css
   Panel administrativo (admin.html) y pantalla de acceso (login.html).
   Misma identidad de marca que el sitio público, pero con densidad de
   información propia de una herramienta de trabajo del taller/auditoría.
   ========================================================================== */

.admin-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
}

.admin-sidebar {
  background: var(--terrae-nogal-900);
  border-right: var(--borde-oro);
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
}

.admin-sidebar__logo {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  margin-bottom: var(--space-5);
}
.admin-sidebar__logo img { height: 30px; }

.admin-nav { list-style: none; margin: 0; padding: 0; flex: 1; }
.admin-nav__item + .admin-nav__item { margin-top: var(--space-1); }
.admin-nav__link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 10px var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-body-sm);
  color: rgba(243, 237, 224, 0.7);
  transition: background var(--duracion-rapida) var(--easing-terrae), color var(--duracion-rapida) var(--easing-terrae);
}
.admin-nav__link:hover { background: rgba(184,147,90,0.08); color: var(--terrae-marfil-050); }
.admin-nav__link[aria-current="page"] {
  background: rgba(15, 157, 99, 0.1);
  color: var(--terrae-esmeralda-500);
  border-left: 2px solid var(--terrae-esmeralda-500);
}

.admin-sidebar__usuario {
  border-top: var(--borde-oro);
  padding-top: var(--space-3);
  font-size: var(--text-body-sm);
}
.admin-sidebar__rol {
  font-size: 0.7rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--terrae-oro-500);
}

.admin-main { padding: var(--space-4); }

.admin-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.admin-kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}
.admin-kpi {
  border: var(--borde-oro);
  padding: var(--space-3);
}
.admin-kpi__valor { font-family: var(--font-display); font-size: 2rem; color: var(--terrae-marfil-050); }
.admin-kpi__label { font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(243,237,224,0.6); }

.admin-panel {
  border: var(--borde-oro);
  padding: var(--space-3);
  margin-bottom: var(--space-4);
}
.admin-panel__titulo {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

/* -------------------------------------------------------------------------
   LOGIN
   ------------------------------------------------------------------------- */
.login-pantalla {
  min-height: 100svh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--terrae-nogal-950);
  padding: var(--space-3);
}

.login-caja {
  width: 100%;
  max-width: 400px;
  border: var(--borde-oro);
  padding: var(--space-5);
  text-align: center;
}

.login-caja__logo { height: 48px; margin-inline: auto var(--space-3); }
.login-caja__titulo { margin-bottom: var(--space-1); }
.login-caja__subtitulo {
  font-size: var(--text-body-sm);
  color: rgba(243,237,224,0.6);
  margin-bottom: var(--space-4);
}

.login-caja form { text-align: left; }

.login-caja__submit { width: 100%; margin-top: var(--space-2); }

.login-caja__aviso {
  margin-top: var(--space-3);
  font-size: 0.75rem;
  color: rgba(243,237,224,0.45);
}
