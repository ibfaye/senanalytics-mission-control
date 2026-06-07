/**
 * Next.js 16 proxy.ts — API route proxy to FastAPI backend.
 * All /api/mission-control/* requests are forwarded here.
 */
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, "GET");
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, "POST");
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, "PUT");
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, "DELETE");
}

async function proxyRequest(
  request: NextRequest,
  path: string[],
  method: string
): Promise<NextResponse> {
  const url = `${BACKEND_URL}/api/${path.join("/")}`;
  const headers = new Headers(request.headers);
  headers.set("X-Forwarded-For", request.headers.get("x-forwarded-for") || "");

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: method !== "GET" ? await request.text() : undefined,
    });

    const data = await response.text();
    return new NextResponse(data, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (error) {
    console.error(`[Proxy] Error forwarding to ${url}:`, error);
    return NextResponse.json(
      { error: "Backend unreachable", detail: String(error) },
      { status: 502 }
    );
  }
}
