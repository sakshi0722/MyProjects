import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  mode: 'login' | 'register' = 'login';

  name = '';
  email = '';
  password = '';
  confirmPassword = '';

  isLoading = false;
  errorMessage = '';

  constructor(
    private auth: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    if (this.auth.isLoggedIn) {
      this.router.navigate(['/dashboard']);
    }
  }

  switchMode(m: 'login' | 'register'): void {
    this.mode = m;
    this.errorMessage = '';
  }

  onSubmit(): void {
    this.errorMessage = '';
    if (this.mode === 'register') {
      this.doRegister();
    } else {
      this.doLogin();
    }
  }

  doRegister(): void {
    if (!this.name.trim()) { this.errorMessage = 'Please enter your name.'; return; }
    if (!this.email.trim()) { this.errorMessage = 'Please enter your email.'; return; }
    if (this.password.length < 6) { this.errorMessage = 'Password must be at least 6 characters.'; return; }
    if (this.password !== this.confirmPassword) { this.errorMessage = 'Passwords do not match.'; return; }

    this.isLoading = true;
    this.auth.register(this.name, this.email, this.password).subscribe({
      next: (res) => {
        this.auth.setUser({ user_id: res.user_id, name: res.name, email: res.email });
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Registration failed. Please try again.';
        this.cdr.detectChanges();
      }
    });
  }

  doLogin(): void {
    if (!this.email.trim()) { this.errorMessage = 'Please enter your email.'; return; }
    if (!this.password) { this.errorMessage = 'Please enter your password.'; return; }

    this.isLoading = true;
    this.auth.login(this.email, this.password).subscribe({
      next: (res) => {
        this.auth.setUser({ user_id: res.user_id, name: res.name, email: res.email });
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Login failed. Please try again.';
        this.cdr.detectChanges();
      }
    });
  }
}
