import { MockedProvider } from "@apollo/client/testing";
import { cleanup, render, screen } from "@testing-library/react";
import { afterAll, describe, expect, it } from "vitest";
import Apollo, { QUERY } from "../../../src/components/tests/branch-list-test";
import { branchesMocks } from "../../../tests/mocks/data/branches";

afterAll(cleanup);

const mocks: any[] = [
  {
    request: {
      query: QUERY,
    },
    result: {
      data: {
        branch: branchesMocks,
      },
    },
  },
];

describe("Branch list", () => {
  it("should query the branch list and display the result", async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <Apollo />
      </MockedProvider>
    );

    expect(await screen.findByText("Loading...")).toBeTruthy();

    expect(await screen.findByText("Working!")).toBeTruthy();
  });
});
