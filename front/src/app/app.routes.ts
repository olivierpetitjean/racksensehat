import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard.component';
import { KioskComponent } from './pages/kiosk.component';
import { LoginComponent } from './pages/login.component';
import { SetupComponent } from './pages/setup.component';
import { authGuard } from './services/auth.guard';
import { kioskGuard } from './services/kiosk.guard';

export const routes: Routes = [
  { path: '', component: DashboardComponent, canActivate: [authGuard] },
  { path: 'kiosk', component: KioskComponent, canActivate: [kioskGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'setup', component: SetupComponent },
  { path: '**', redirectTo: '' },
];
