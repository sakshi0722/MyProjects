import { Routes } from '@angular/router';
import { EmergencyComponent } from './emergency/emergency.component';
import { MinorInjuryComponent } from './minor-injury/minor-injury.component';
import { RecoveryPageComponent } from './recovery/recovery.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HistoryComponent } from './history/history.component';
import { AuthGuard } from './auth/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'history', component: HistoryComponent, canActivate: [AuthGuard] },
  { path: 'emergency', component: EmergencyComponent, canActivate: [AuthGuard] },
  { path: 'recovery', component: RecoveryPageComponent, canActivate: [AuthGuard] },
  { path: 'minor', component: MinorInjuryComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: 'login' }
];