import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopNavigation from './TopNavigation';

export default function AppFrame() {
  return (
    <div className="cp-shell relative min-h-screen overflow-x-hidden">
      <TopNavigation />

      <main className="mx-auto max-w-[1860px] px-3 pb-6 pt-2 sm:px-4 lg:px-5 lg:pt-1.5">
        <div className="grid gap-3 lg:grid-cols-[264px_minmax(0,1fr)] xl:gap-4">
          <Sidebar />

          <div className="min-w-0 pb-2">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
