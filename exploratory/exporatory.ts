import * as schema from "./schema";

// Pensar fix: Require authenticated requester and authorization checks to prevent unauthorized user deletions
type Requester = {
  id: string;
  role?: string; // e.g., "admin" or undefined
  isAuthenticated: boolean;
};

export async function deleteUser(userId: string, requester: Requester) {
  if (!requester?.isAuthenticated) {
    throw new Error("Unauthorized: user must be authenticated");
  }

  // Only allow users to delete themselves, or admins to delete any user
  if (requester.id !== userId && requester.role !== "admin") {
    throw new Error("Forbidden: insufficient permissions to delete user");
  }

  await db.delete(schema.users.userId).where(eq(schema.users.id, userId));
}