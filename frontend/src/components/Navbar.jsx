import React from 'react';
import { NavLink } from 'react-router-dom';
import { Settings } from 'lucide-react';
import clsx from 'clsx';

const Navbar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Tasks', path: '/tasks' },
    { name: 'Employees', path: '/employees' },
    { name: 'Recommendations', path: '/recommendations' },
  ];

  return (
    <nav className="bg-primary-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <img src="/logo.png" alt="TITANS" className="h-12 object-contain" />
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-4">
              {navItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={({ isActive }) =>
                    clsx(
                      'px-3 py-2 rounded-md text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary-500 text-white border-b-2 border-accent'
                        : 'text-gray-300 hover:bg-primary-500 hover:text-white'
                    )
                  }
                >
                  {item.name}
                </NavLink>
              ))}
              <NavLink
                to="/settings"
                className={({ isActive }) =>
                  clsx(
                    'p-2 rounded-md transition-colors',
                    isActive
                      ? 'bg-primary-500 text-white'
                      : 'text-gray-300 hover:bg-primary-500 hover:text-white'
                  )
                }
                title="Settings"
              >
                <Settings size={20} />
              </NavLink>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
