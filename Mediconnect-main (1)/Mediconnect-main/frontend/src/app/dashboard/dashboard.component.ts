import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { AuthService } from '../auth/auth.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, HttpClientModule, DatePipe],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  user: any = null;
  stats: any = null;
  recentRecovery: any = null;
  recentInjury: any = null;
  dailyTip = '';
  isLoading = true;
  greeting = '';
  today = new Date();
  firstName = '';

  private apiUrl = environment.apiUrl;

  modules = [
    { title: 'Emergency', icon: '🚨', desc: 'Find nearest hospitals, voice search, ambulance contacts', route: '/emergency', color: '#dc2626', bg: '#fef2f2', border: '#fca5a5', isChatbot: false },
    { title: 'Minor Injury', icon: '🩹', desc: 'Upload injury photo for instant AI first aid guidance', route: '/minor', color: '#059669', bg: '#f0fdf4', border: '#86efac', isChatbot: false },
    { title: 'Recovery Planner', icon: '🏥', desc: 'Get a personalised 7-day Indian diet + exercise plan', route: '/recovery', color: '#1d4ed8', bg: '#eff6ff', border: '#93c5fd', isChatbot: false },
    { title: 'MediBot', icon: '💬', desc: 'Ask any health question — available 24/7', route: null, color: '#7c3aed', bg: '#faf5ff', border: '#c4b5fd', isChatbot: true }
  ];

  constructor(
    private auth: AuthService,
    private http: HttpClient,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.user = this.auth.currentUser;
    this.firstName = this.user?.name?.split(' ')[0] || 'there';
    this.setGreeting();
    this.loadDashboard();
  }

  setGreeting(): void {
    const h = new Date().getHours();
    if (h < 12) this.greeting = 'Good Morning';
    else if (h < 17) this.greeting = 'Good Afternoon';
    else this.greeting = 'Good Evening';
  }

  loadDashboard(): void {
    const userId = this.auth.userId;
    this.http.get<any>(`${this.apiUrl}/api/dashboard/stats/${userId}`).subscribe({
      next: (data) => {
        this.stats = data.stats;
        this.recentRecovery = data.recent_recovery;
        this.recentInjury = data.recent_injury;
        this.dailyTip = data.daily_tip;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoading = false; this.cdr.detectChanges(); }
    });
  }

  openChatbot(): void {
    window.dispatchEvent(new CustomEvent('open-medibot'));
  }

  navigateTo(route: string | null, isChatbot: boolean): void {
    if (isChatbot) { this.openChatbot(); return; }
    if (route) this.router.navigate([route]);
  }

  logout(): void { this.auth.logout(); }

  getInitials(): string {
    if (!this.user?.name) return 'U';
    return this.user.name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2);
  }
}
