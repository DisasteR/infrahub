import { expect, test } from "@playwright/test";
import { ACCOUNT_STATE_PATH } from "../constants";
import { createBranch } from "../utils";

test.describe("Branches creation and deletion", () => {
  test.beforeEach(async function ({ page }) {
    page.on("response", async (response) => {
      if (response.status() === 500) {
        await expect(response.url()).toBe("This URL responded with a 500 status");
      }
    });
  });

  test.describe("when not logged in", () => {
    test("should not be able to create a branch if not logged in", async ({ page }) => {
      await page.goto("/");
      await page.getByTestId("branch-selector-trigger").click();
      await expect(page.getByTestId("create-branch-button")).toBeDisabled();
    });

    test("should not show quick-create option when searching for non-existent branch", async ({
      page,
    }) => {
      await page.goto("/");
      await page.getByTestId("branch-selector-trigger").click();

      const nonExistentBranchName = "non-existent-branch-123";
      await page.getByTestId("branch-search-input").fill(nonExistentBranchName);

      await expect(page.getByText("No branch found")).toBeVisible();
      await expect(
        page.getByRole("option", { name: `Create branch ${nonExistentBranchName}` })
      ).not.toBeVisible();
    });
  });

  test.describe("when logged in as Admin", () => {
    test.describe.configure({ mode: "serial" });
    test.use({ storageState: ACCOUNT_STATE_PATH.ADMIN });

    test("should create a new branch", async ({ page }) => {
      await page.goto("/");
      await page.getByTestId("branch-selector-trigger").click();
      await page.getByTestId("create-branch-button").click();

      // Form
      await expect(page.getByText("Create a new branch")).toBeVisible();
      await page.getByLabel("New branch name *").fill("test123");
      await page.getByText("New branch description").fill("branch creation test");
      await page.getByRole("button", { name: "Create a new branch" }).click();

      // After submit
      await expect(page.getByTestId("branch-selector-trigger")).toContainText("test123");
      await expect(page).toHaveURL(/.*?branch=test123/);
    });

    test("should display the new branch", async ({ page }) => {
      await page.goto("/");
      await page.getByTestId("branch-selector-trigger").click();
      await expect(page.getByTestId("branch-list")).toContainText("test123");

      await page.getByRole("link", { name: "View all branches" }).click();
      await expect(page).toHaveURL(/.*\/branches/);

      await page.getByTestId("branches-items").getByText("test123").click();
      await expect(page.getByText("Nametest123")).toBeVisible();
      expect(page.url()).toContain("/branches/test123");
    });

    test("create a new branch for next step", async ({ page }) => {
      await page.goto("/");
      await createBranch(page, "test456");
    });

    test("should delete a non-selected branch and remain on the current branch", async ({
      page,
    }) => {
      await page.goto("/branches/test456?branch=test123");

      await page.getByRole("button", { name: "Delete" }).click();

      const modalDelete = page.getByTestId("modal-delete");
      await expect(modalDelete.getByRole("heading", { name: "Delete" })).toBeVisible();
      await expect(
        modalDelete.getByText("Are you sure you want to remove the branch `test456`?")
      ).toBeVisible();
      await modalDelete.getByRole("button", { name: "Delete" }).click();

      // we should stay on the branch test123
      await expect(page.getByTestId("branch-selector-trigger")).toContainText("test123");
      await page.getByTestId("branch-selector-trigger").click();
      await expect(page.getByTestId("branch-list")).toContainText("test123");
      await expect(page.getByTestId("branch-list")).not.toContainText("test456");
      expect(page.url()).toContain("/branches?branch=test123");
    });

    test("should delete the currently selected branch", async ({ page }) => {
      await page.goto("/branches");
      await page.getByText("test123").click();
      await page.getByRole("button", { name: "Delete" }).click();
      await page.getByTestId("modal-delete-confirm").click();

      expect(page.url()).toContain("/branches");
      await page.getByTestId("branch-selector-trigger").click();
      await expect(page.getByTestId("branch-list")).not.toContainText("test123");
    });

    test("allow to create a branch with a name that does not exists", async ({ page }) => {
      await page.goto("/");
      await page.getByTestId("branch-selector-trigger").click();
      await page.getByTestId("branch-search-input").fill("quick-branch-form");
      await page.getByRole("option", { name: "Create branch quick-branch-form" }).click();
      await expect(page.getByLabel("New branch name *")).toHaveValue("quick-branch-form");
    });
  });
});
