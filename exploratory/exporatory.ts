import * as schema from "./schema";

// Define a User type for authorization context. Adjust according to your actual user structure.
interface User {
  id: string;
  role?: string; // e.g., 'admin'
}

/**
 * Deletes a user if the currentUser is authorized.
 * Only admins or the user themselves can delete the account.
 * @param userId - The user ID of the account to delete
 * @param currentUser - The currently authenticated user performing the operation
 * @throws Error if the current user is not authenticated or not authorized
 */
export async function deleteUser(userId: string, currentUser: User | null) {
  if (!currentUser || !currentUser.id) {
    throw new Error("Authentication required.");
  }
  const isAdmin = currentUser.role === "admin";
  const isSelf = currentUser.id === userId;

  if (!isAdmin && !isSelf) {
    throw new Error("Not authorized to delete this user.");
  }

  await db.delete(schema.users.userId).where(eq(schema.users.id, userId));
}