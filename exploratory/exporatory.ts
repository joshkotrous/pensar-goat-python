import * as schema from "./schema";

/**
 * Deletes a user account.
 * Only the user themselves or an administrator can perform this action.
 * @param requestingUser The authenticated user performing the operation.
 * @param userId The ID of the user account to be deleted.
 * @throws {Error} If the requesting user does not have permission.
 */
export async function deleteUser(
  requestingUser: { id: string; isAdmin: boolean },
  userId: string
) {
  // Authorization check: Only allow deletion if the requesting user is an admin or is deleting themselves
  if (
    !requestingUser.isAdmin &&
    requestingUser.id !== userId
  ) {
    throw new Error("Unauthorized: only account owners or administrators can delete user accounts.");
  }

  await db.delete(schema.users.userId).where(eq(schema.users.id, userId));
}