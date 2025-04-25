import * as schema from "./schema";

export async function deleteUser(userId: string) {
  await db.delete(schema.users.userId).where(eq(schema.users.id, userId));
}
