import { NavLink, Outlet } from 'react-router-dom';

const LINKS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/employees', label: 'Employees' },
  { to: '/departments', label: 'Departments' },
];

export default function Layout() {
  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar__inner">
          <span className="brand">Employee Management</span>
          <nav className="nav" aria-label="Main">
            {LINKS.map((l) => (
              <NavLink key={l.to} to={l.to} className={({ isActive }) => `nav__link${isActive ? ' nav__link--active' : ''}`}>
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </div>
  );
}
