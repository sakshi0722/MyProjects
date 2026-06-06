import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../auth/auth.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss']
})
export class HistoryComponent implements OnInit {
  activeTab: 'emergency' | 'injury' | 'recovery' | 'chat' = 'emergency';

  emergencyLogs: any[] = [];
  injuryLogs: any[] = [];
  recoveryPlans: any[] = [];
  chatLogs: any[] = [];

  isLoading = false;
  private apiUrl = environment.apiUrl;
  private userId = '';

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.userId = this.auth.userId;
    this.loadTab('emergency');
  }

  loadTab(tab: 'emergency' | 'injury' | 'recovery' | 'chat'): void {
    this.activeTab = tab;
    this.isLoading = true;

    const urls: Record<string, string> = {
      emergency: `${this.apiUrl}/api/emergency/logs/${this.userId}`,
      injury: `${this.apiUrl}/api/minor-injury/history/${this.userId}`,
      recovery: `${this.apiUrl}/api/recovery/plans/${this.userId}`,
      chat: `${this.apiUrl}/api/chatbot/history/${this.userId}`
    };

    this.http.get<any[]>(urls[tab]).subscribe({
      next: (data) => {
        if (tab === 'emergency') this.emergencyLogs = data;
        if (tab === 'injury') this.injuryLogs = data;
        if (tab === 'recovery') this.recoveryPlans = data;
        if (tab === 'chat') this.chatLogs = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoading = false; this.cdr.detectChanges(); }
    });
  }

  goBack(): void { this.router.navigate(['/dashboard']); }

  getSeverityClass(severity: string): string {
    if (!severity) return '';
    const s = severity.toLowerCase();
    if (s.includes('severe') || s.includes('high')) return 'badge-red';
    if (s.includes('moderate') || s.includes('medium')) return 'badge-yellow';
    return 'badge-green';
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });
    } catch { return dateStr; }
  }
}