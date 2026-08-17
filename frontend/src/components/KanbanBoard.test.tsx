import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { mockBoardData, mockFetchSuccess } from "@/test/mocks/api";

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    // Mock the fetch API for all tests
    global.fetch = vi.fn((url: string, options?: any) => {
      const method = options?.method || 'GET';
      
      if (url.includes('/api/board')) {
        return mockFetchSuccess(mockBoardData);
      }
      if (url.includes('/api/cards') && method === 'PUT') {
        return mockFetchSuccess({});
      }
      if (url.includes('/api/cards') && method === 'DELETE') {
        return mockFetchSuccess({});
      }
      if (url.includes('/api/cards') && method === 'POST') {
        return mockFetchSuccess({ 
          id: 'card-new', 
          title: 'New card', 
          details: 'Notes' 
        });
      }
      if (url.includes('/api/columns')) {
        return mockFetchSuccess({});
      }
      return mockFetchSuccess({});
    }) as any;
  });

  it("renders five columns", async () => {
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });

    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });

    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    await waitFor(() => {
      expect(within(column).getByText("New card")).toBeInTheDocument();
    });

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    await waitFor(() => {
      expect(within(column).queryByText("New card")).not.toBeInTheDocument();
    });
  });
});
