import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Public routes that don't need auth
  const isPublicRoute = pathname === '/login' || pathname.startsWith('/_next') || pathname.includes('/api/');
  
  if (isPublicRoute) {
    return NextResponse.next();
  }

  // Check for the user_role in cookies (Middleware can't access localStorage)
  const userRole = request.cookies.get('user_role')?.value;

  if (!userRole) {
    // If no role found, redirect to login
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Admin route protection
  if (pathname.startsWith('/admin') && userRole !== 'admin') {
    const homeUrl = new URL('/', request.url);
    return NextResponse.redirect(homeUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
