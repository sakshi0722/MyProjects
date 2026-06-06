import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface User {
  user_id: string;
  name: string;
  email: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = environment.apiUrl;
  private userSubject = new BehaviorSubject<User | null>(this.loadUser());
  user$ = this.userSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  private loadUser(): User | null {
    try {
      const u = sessionStorage.getItem('mediconnect_user');
      return u ? JSON.parse(u) : null;
    } catch { return null; }
  }

  get currentUser(): User | null { return this.userSubject.value; }
  get isLoggedIn(): boolean { return !!this.userSubject.value; }
  get userId(): string { return this.userSubject.value?.user_id || 'user_001'; }

  register(name: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/auth/register`, { name, email, password });
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/auth/login`, { email, password });
  }

  setUser(user: User): void {
    sessionStorage.setItem('mediconnect_user', JSON.stringify(user));
    this.userSubject.next(user);
  }

  logout(): void {
    sessionStorage.removeItem('mediconnect_user');
    this.userSubject.next(null);
    this.router.navigate(['/login']);
  }
}
